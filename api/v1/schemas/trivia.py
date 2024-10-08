from pydantic import BaseModel, Field
from datetime import datetime
from api.v1.schemas.african_countries_enum import AfricanCountriesEnum as ACE
from api.v1.schemas.submission import DifficultyEnum, CategoryEnum
from api.v1.schemas.base_schemas import BaseSuccessResponseSchema


class TriviaBaseSchema(BaseModel):
    question: str = Field(min_length=1)
    incorrect_options: list[str] = Field(min_length=3, max_length=3)
    correct_option: str = Field(min_length=1)
    difficulty: DifficultyEnum


class HelperSchemaTwo(TriviaBaseSchema):
    category: CategoryEnum
    countries: list[ACE] = Field(default=[])


class CreateTriviaSchema(HelperSchemaTwo):
    submission_id: str | None = Field(min_length=36, max_length=36, default=None)


class UpdateTriviaSchema(BaseModel):
    question: str | None = Field(min_length=1, default=None)
    incorrect_options: list[str] | None = Field(
        min_length=3, max_length=3, default=None
    )
    correct_option: str | None = Field(min_length=1, default=None)
    difficulty: DifficultyEnum | None = None

    category: CategoryEnum | None = None
    countries: list[ACE] | None = Field(default=None)


class HelperResponseSchemaOne(CreateTriviaSchema):
    id: str
    created_at: datetime


class RetrieveTriviaForModSchema(HelperResponseSchemaOne, TriviaBaseSchema):
    pass


class GetTriviaForModResponseModelSchema(BaseSuccessResponseSchema):
    data: RetrieveTriviaForModSchema


class GetListOfTriviaForModResponseModelSchema(BaseSuccessResponseSchema):
    data: list[RetrieveTriviaForModSchema]


class GetListOfTriviaUsersResponseModelSchema(BaseSuccessResponseSchema):
    data: list[HelperSchemaTwo] | None
