from pydantic import BaseModel, Field, EmailStr, StringConstraints
from typing import Annotated
from datetime import datetime
from api.v1.schemas.african_countries_enum import AfricanCountriesEnum as ACE
from api.v1.schemas.base_schemas import BaseSuccessResponseSchema


class ModeratorLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class ModeratorBaseSchema(BaseModel):
    email: EmailStr
    first_name: str = Annotated[
        str, StringConstraints(min_length=2, max_length=30, strip_whitespace=True)
    ]
    last_name: str = Annotated[
        str, StringConstraints(min_length=2, max_length=30, strip_whitespace=True)
    ]
    username: str = Annotated[
        str, StringConstraints(min_length=2, max_length=30, strip_whitespace=True)
    ]
    country_preferences: None | list[ACE] = Field(min_length=1, default=[])


class CreateModeratorSchema(ModeratorBaseSchema):
    password: Annotated[
        str, StringConstraints(min_length=3, max_length=64, strip_whitespace=True)
    ]


class CreateModeratorResponseSchema(ModeratorBaseSchema):
    id: str
    updated_at: datetime
    is_admin: bool
    is_active: bool

    class Config:
        from_attributes = True


class CreateModeratorResponseModelSchema(
    BaseSuccessResponseSchema, CreateModeratorResponseSchema
):
    pass


class UpdateModeratorSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    password: str | None = None
    country_preferences: None | list[ACE] = Field(min_length=1, default=[])


class UpdateModeratorByAdminSchema(UpdateModeratorSchema):
    is_admin: bool | None = None


class DeactivateModeratorSchema(BaseModel):
    is_active: bool
