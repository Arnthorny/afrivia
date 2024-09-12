from pydantic import BaseModel, Field, EmailStr
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


class SubmissionBaseSchema(BaseModel):
    question: str = Field(min_length=1)
    incorrect_options: list[str] = Field(min_length=3, max_length=3)
    correct_option: str = Field(min_length=1)
    difficulty: DifficultyEnum
    submission_note: str | None = None


class CreateSubmissionSchema(SubmissionBaseSchema):
    category: CategoryEnum
    countries: list[ACE] = Field(default=[])


class PostSubmissionResponseSchema(SubmissionBaseSchema):
    id: str
    status: str
    moderator_id: str
    updated_at: datetime
    category: CategoryEnum
    countries: list[ACE] = Field(default=[])


class PostSubmissionResponseModelSchema(BaseSuccessResponseSchema):
    data: PostSubmissionResponseSchema
