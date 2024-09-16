from pydantic import BaseModel, Field
from datetime import datetime
from api.v1.schemas.african_countries_enum import AfricanCountriesEnum as ACE
from api.v1.schemas.base_schemas import BaseSuccessResponseSchema
from enum import Enum


class DifficultyEnum(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class SubmissionStatusEnum(str, Enum):
    awaiting = "awaiting"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class CategoryEnum(str, Enum):
    entertainment = "Entertainment"
    sports = "Sports"
    general_knowledge = "General Knowledge"
    science = "Science"
    mythology = "Mythology"
    geography = "Geography"
    history = "History"
    politics = "Politics"
    art = "Art"
    celebrity = "Celebrities"
    animals = "Animals"
    folklore = "Folklore"
    language = "Language"
    food_drinks = "Food and Drinks"


class SubmissionBaseSchema(BaseModel):
    question: str = Field(min_length=1)
    incorrect_options: list[str] = Field(min_length=3, max_length=3)
    correct_option: str = Field(min_length=1)
    difficulty: DifficultyEnum
    submission_note: str | None = None


class CreateSubmissionSchema(SubmissionBaseSchema):
    category: CategoryEnum
    countries: list[ACE] = Field(default=[])


class HelperResponseSchemaOne(CreateSubmissionSchema):
    id: str
    status: str
    created_at: datetime


class PostSubmissionResponseSchema(HelperResponseSchemaOne, SubmissionBaseSchema):
    moderator_id: str


class RetrieveSubmissionForModSchema(HelperResponseSchemaOne, SubmissionBaseSchema):
    pass


class PaginatedBaseSchema(BaseModel):
    page: int
    total_pages: int
    total: int
    limit: int
    items: list[RetrieveSubmissionForModSchema]


class PaginatedResponseModelSchema(BaseSuccessResponseSchema):
    data: PaginatedBaseSchema


class PostSubmissionResponseModelSchema(BaseSuccessResponseSchema):
    data: PostSubmissionResponseSchema


class GetSubmissionForModResponseModelSchema(BaseSuccessResponseSchema):
    data: RetrieveSubmissionForModSchema


class GetListOfSubmissionForModResponseModelSchema(BaseSuccessResponseSchema):
    data: list[RetrieveSubmissionForModSchema]
