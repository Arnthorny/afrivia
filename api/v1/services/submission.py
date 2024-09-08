from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from api.v1.models.submission import Submission, SubmissionOption
from api.core.base.services import Service
from api.v1.schemas import submission as s_schema
from api.v1.services.country import CountryService
from api.v1.services.category import CategoryService

from api.v1.models.moderator import Moderator





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

    def create(self, db: Session, schema: s_schema.CreateSubmissionSchema) -> Submission:
        """Creates a new submission


        Args:
            db (Session): Database session
            schema (s_schema.CreateSubmissionSchema): Pydantic Schema

        Returns:
            Submission: Return newly created submission
        """

        try:
            schema_dump = schema.model_dump()
            countries = schema_dump.pop('countries', [])
            country_models_list = CountryService.fetch_countries(db, countries)

            given_category = schema_dump.pop('category')

            category_list = CategoryService.fetch_categories(db, [given_category])

            all_options = schema_dump.pop('incorrect_options')
            all_options.append(schema_dump.pop('correct_option'))
            


            sub = Submission(**schema_dump)
            sub.countries = country_models_list
            sub.categories = category_list

            self.set_submission_options(sub, all_options)

            mod = self.find_suitable_mod(db, sub)
            sub.moderator = mod

            db.add(sub)
            db.commit()
            db.refresh(sub)

            return sub
    

        except IntegrityError as e:
            raise HTTPException(
                status_code=400,
                detail="This question already exists",
        )

    def find_suitable_mod(self, db:Session, sub: Submission):
        # TODO Upgrade algorithm
        bob_mod = db.query(Moderator).filter(Moderator.first_name == 'Bob').first()

        return bob_mod
    

    def set_submission_options(self, sub: Submission, all_options: list[str]):
        all_opt_obj = [
                SubmissionOption(content=all_options[0]),
                SubmissionOption(content=all_options[1]),
                SubmissionOption(content=all_options[2]),
                SubmissionOption(content=all_options[3], is_correct=True),
            ]
            
        sub.options = all_opt_obj


submission_service = SubmissionService()