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


class CreateTriviaSchema(TriviaBaseSchema):
    category: CategoryEnum
    countries: list[ACE] = Field(default=[])


class HelperResponseSchemaOne(CreateTriviaSchema):
    id: str
    created_at: datetime


class RetrieveTriviaForModSchema(HelperResponseSchemaOne, TriviaBaseSchema):
    pass


class GetTriviaForModResponseModelSchema(BaseSuccessResponseSchema):
    data: RetrieveTriviaForModSchema


class GetListOfTriviaForModResponseModelSchema(BaseSuccessResponseSchema):
    data: list[RetrieveTriviaForModSchema]
