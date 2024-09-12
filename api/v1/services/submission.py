from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from api.utils.paginated_response import paginated_response
from api.v1.models.submission import Submission, SubmissionOption
from api.core.base.services import Service
from api.v1.schemas import submission as s_schema
from api.v1.services.country import CountryService
from api.v1.services.category import CategoryService

from api.v1.models.moderator import Moderator
from api.v1.models.country import Country
from api.v1.models.category import Category
from api.utils.logger import logger
from api.utils.sql_queries import query_for_mods_pref_submissions


class SubmissionService(Service):
    """Service class for handling submissions

    Args:
        Service (_type_): Abstract Service to inherit from
    """

    def update(self):
        pass

    def delete(self):
        pass

    def fetch_all():
        pass

    def fetch(self, db: Session, id: str):
        pass

    def extract_countries_categories_options(
        self, schema_d: dict, db: Session
    ) -> tuple[list[Country], list[Category], list[SubmissionOption]]:
        """This method extracts and converts countries, categories and options
            present in the schema dump into sqlalchemy models

        Args:
            schema_d (dict): Dictionary containing schema dump to be used
            db (Session): Database session
        Returns:
            tuple: A tuple containing a list of extracted models (countries, categories and options)
        """
        try:
            countries = schema_d.pop("countries", [])
            country_models_list = CountryService.fetch_countries(db, countries)

            given_category = schema_d.pop("category")
            category_models_list = CategoryService.fetch_categories(
                db, [given_category]
            )

            all_options = schema_d.pop("incorrect_options")
            all_options.append(schema_d.pop("correct_option"))

            options_models_list = [
                SubmissionOption(content=all_options[0]),
                SubmissionOption(content=all_options[1]),
                SubmissionOption(content=all_options[2]),
                SubmissionOption(content=all_options[3], is_correct=True),
            ]

            return (country_models_list, category_models_list, options_models_list)

        except Exception as e:
            logger.exception(e)

    def create(
        self, db: Session, schema: s_schema.CreateSubmissionSchema
    ) -> Submission:
        """Creates a new submission


        Args:
            db (Session): Database session
            schema (s_schema.CreateSubmissionSchema): Pydantic Schema

        Returns:
            Submission: Return newly created submission
        """
        try:
            schema_dump = schema.model_dump()
            assoc_countries_copy = schema_dump.get("countries", []).copy()

            [country_models_list, category_models_list, options_models_list] = (
                self.extract_countries_categories_options(schema_dump, db)
            )

            sub = Submission(**schema_dump)
            sub.countries = country_models_list
            sub.categories = category_models_list
            sub.options = options_models_list

            mod_id = self.find_suitable_mod(db, assoc_countries_copy)
            sub.moderator_id = mod_id

            db.add(sub)
            db.commit()
            db.refresh(sub)

            return sub

        except IntegrityError as e:
            raise HTTPException(
                status_code=400,
                detail="This question already exists",
            )

        except Exception as e:
            logger.exception(e)

    def get_mod_prefs_and_assigns(self, db: Session) -> list[tuple[str, list, int]]:
        """This function uses sql queries to retrieve details of moderators
        present on the database. These details are used to determine what mod
        is assigned to a new submission in the database

        Args:
            db (Session): The database session

        Returns:
            list[tuple[str, list, int]]: This a list of tuples which contains the moderator's id,
            a list of their preferred countries and the number of submissions pending their review.
            It is ordered by the pending submission count
        """
        try:
            query_obj = query_for_mods_pref_submissions()
            result = db.execute(query_obj)
            return result.all()
        except Exception as e:
            logger.exception(e)

    def find_suitable_mod(self, db: Session, assoc_countries: list) -> str:
        """Function to detetmin what moderator is suitable to be assigned
        for a given submission made to the db.

        Args:
            db (Session): Database of session object
            assoc_countries (list): countries associated with submission

        Returns:
            str: The id of the selected moderator
        """
        try:
            all_mod_details = self.get_mod_prefs_and_assigns(db)
            if len(assoc_countries) == 0:
                # If no countries associated with submission, simply assign to mod
                # with lowest pending assigns
                return all_mod_details[0][0]

            for mod_id, mod_cntry_pref, pending_count in all_mod_details:
                if len(mod_cntry_pref) == 0 or set(mod_cntry_pref).intersection(
                    assoc_countries
                ):
                    return mod_id

        except Exception as e:
            logger.exception(e)

    def fetch_paginated(
        self, db: Session, skip: int, limit: int, filters: dict[str]
    ) -> dict[str]:

        page_number = int(skip / limit) + 1

        resp = paginated_response(
            db=db, model=Submission, skip=skip, limit=limit, filters=filters
        )

        resp.pop("skip", None)
        resp["page"] = page_number

        resp["items"] = list(
            map(
                lambda x: s_schema.RetrieveSubmissionForModSchema.model_validate(
                    x.to_dict()
                ),
                resp["results"],
            )
        )

        resp.pop("results", None)

        return resp


submission_service = SubmissionService()
