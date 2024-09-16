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

from api.v1.models.country import Country
from api.v1.models.category import Category
from api.utils.logger import logger


class TriviaService(Service):
    """Service class for handling trivias

    Args:
        Service (_type_): Abstract Service to inherit from
    """

    NOT_FOUND_EXC = HTTPException(
        status_code=404,
        detail="Trivia not found",
    )

    FORBIDDEN_EXC = HTTPException(
        status_code=403,
        detail="You do not have permission to access this resource",
    )

    def fetch_all(self, db: Session) -> list[Trivia]:
        """Fetches all trivias from the database

        Args:
            db (Session): Db session object

        Returns:
            list[Trivia]: A list of all trivia objects on the database
        """
        all_trivias = db.query(Trivia).all()
        return all_trivias

    def fetch(self, db: Session, id: str, raise_404=False) -> Trivia | None:
        """Fetches a Trivia by their id"""

        trivia = db.get(Trivia, id)

        if trivia is None and raise_404 is True:
            raise self.NOT_FOUND_EXC

        return trivia

    def extract_options(self, schema_d: dict) -> list[TriviaOption]:
        """This  function extract all options from a given schema dictionary.
        This dictionary might result from a create endpoint or an update endpoint.
        As such, the list returned may contain either 4 elements - for a full update or a create request, 3 element - for an update of just the incorrect options, 1 element - for an update of the correct option, 0 elements - an update which doesn't affect the options

        Args:
            schema_d (dict): Schema dump dictionary to be used

        Returns:
            list[TriviaOption]: A variable length array which contains the trivia options models in order of [incorrect, incorrect, incorrect, correct] if all are available,
            [incorrect, incorrect, incorrect] if 3 were available in dump,
            [correct] if 1 was available in dump.
        """
        all_options: list[str] = schema_d.pop("incorrect_options", [])
        all_options.append(schema_d.pop("correct_option", None))

        options_models_list: list[TriviaOption] = []

        # Append incorrect options first, if any
        for option in all_options[0:3]:
            options_models_list.append(TriviaOption(content=option))

        # Append correct option(last element) if it is not None.
        if all_options[-1] is not None:
            options_models_list.append(
                TriviaOption(content=all_options[-1], is_correct=True)
            )

        return options_models_list

    def extract_countries_categories_options(
        self, schema_d: dict, db: Session
    ) -> tuple[list[Country] | None, list[Category] | None, list[TriviaOption]]:
        """This method extracts and converts countries, categories and options
            present in the schema dump into sqlalchemy models

        Args:
            schema_d (dict): Dictionary containing schema dump to be used
            db (Session): Database session
        Returns:
            tuple: A tuple containing a list of extracted models or None if not specified (countries, categories and options)
        """
        try:
            countries = schema_d.pop("countries", None)
            country_models_list = CountryService.fetch_countries(db, countries)

            given_category = schema_d.pop("category", None)
            given_category_list = (
                [given_category] if given_category is not None else None
            )

            category_models_list = CategoryService.fetch_categories(
                db, given_category_list
            )

            # Extract Options
            options_models_list = self.extract_options(schema_d)

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

    def update(self, db: Session, schema: t_schema.UpdateTriviaSchema, id: str):
        """Updates an existing Trivia
        Args:
            db (Session): Database session
            schema (s_schema.CreateTriviaSchema): Pydantic Schema

        Returns:
            Trivia: Return newly created Trivia
        """
        try:
            trivia = self.fetch(db=db, id=id, raise_404=True)
            schema_dump = schema.model_dump(exclude_unset=True)

            [country_models_list, category_models_list, options_models_list] = (
                self.extract_countries_categories_options(schema_dump, db)
            )

            # Update all other fields with the provided schema data
            for key, value in schema_dump.items():
                setattr(trivia, key, value)

            # The above may not all be present in the extract from the schema dump for an update

            if country_models_list is not None:
                trivia.countries = country_models_list
            if category_models_list is not None:
                trivia.categories = category_models_list

            if options_models_list is not None and options_models_list != []:
                existing_options: list[TriviaOption] = trivia.options
                for i, existing_option in enumerate(existing_options):
                    # Find and update correct option model first, if applicable
                    if (
                        existing_option.is_correct
                        and options_models_list[-1].is_correct
                    ):
                        existing_option.content = options_models_list[-1].content
                        continue

                    existing_option.content = options_models_list[i].content

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
            raise e

    def delete(self, db: Session, id: str) -> bool:
        """Deletes an existing Trivia. Else raise a 404 if not found"""
        try:
            trivia = self.fetch(db=db, id=id, raise_404=True)

            db.delete(trivia)
            db.commit()

            return True
        except Exception as e:
            logger.exception(e)
            raise e


trivia_service = TriviaService()
