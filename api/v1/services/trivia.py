from typing import Literal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from api.core.base.services import Service

from api.utils.paginated_response import paginated_response
from api.v1.models.trivia import Trivia, TriviaOption
from api.v1.schemas import trivia as t_schema
from api.v1.services.country import CountryService
from api.v1.services.category import CategoryService

from api.v1.models.moderator import Moderator
from api.v1.models.country import Country
from api.v1.models.category import Category
from api.utils.logger import logger
from api.utils.sql_queries import query_for_mods_pref_submissions


class TriviaService(Service):
    """Service class for handling submissions

    Args:
        Service (_type_): Abstract Service to inherit from
    """

    NOT_FOUND_EXC = HTTPException(
        status_code=404,
        detail="Submission not found",
    )

    FORBIDDEN_EXC = HTTPException(
        status_code=403,
        detail="You do not have permission to access this resource",
    )

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
    ) -> tuple[list[Country], list[Category], list[TriviaOption]]:
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
                TriviaOption(content=all_options[0]),
                TriviaOption(content=all_options[1]),
                TriviaOption(content=all_options[2]),
                TriviaOption(content=all_options[3], is_correct=True),
            ]

            return (country_models_list, category_models_list, options_models_list)

        except Exception as e:
            logger.exception(e)

    def create(self, db: Session, schema: t_schema.CreateTriviaSchema) -> Trivia:
        """Creates a new Trivia


        Args:
            db (Session): Database session
            schema (s_schema.CreateTriviaSchema): Pydantic Schema

        Returns:
            Trivia: Return newly created Trivia
        """
        try:
            schema_dump = schema.model_dump()

            [country_models_list, category_models_list, options_models_list] = (
                self.extract_countries_categories_options(schema_dump, db)
            )

            trivia = Trivia(**schema_dump)
            trivia.countries = country_models_list
            trivia.categories = category_models_list
            trivia.options = options_models_list

            db.add(trivia)
            db.commit()
            db.refresh(trivia)

            return trivia

        except IntegrityError as e:
            raise HTTPException(
                status_code=400,
                detail="This trivia already exists",
            )

        except Exception as e:
            logger.exception(e)
