from pydantic import BaseModel, Field, EmailStr, StringConstraints, ConfigDict
from typing import Annotated
from datetime import datetime
from api.v1.schemas.african_countries_enum import AfricanCountriesEnum as ACE
from api.v1.schemas.base_schemas import BaseSuccessResponseSchema


class ModeratorLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class ModeratorLogoutResponse(BaseSuccessResponseSchema):
    pass


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
    country_preferences: list[ACE] = Field(default=[])


class CreateModeratorSchema(ModeratorBaseSchema):
    password: Annotated[
        str, StringConstraints(min_length=3, max_length=64, strip_whitespace=True)
    ]


class CreateModeratorResponseSchema(ModeratorBaseSchema):
    id: str
    created_at: datetime
    is_admin: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class DataModeratorResponseSchema(BaseModel):
    data: CreateModeratorResponseSchema


class CreateModeratorResponseModelSchema(
    BaseSuccessResponseSchema, DataModeratorResponseSchema
):
    access_token: str
    refresh_token: str


class GetModeratorResponseModelSchema(
    BaseSuccessResponseSchema, DataModeratorResponseSchema
):
    pass


class RefreshAccessTokenResponse(BaseSuccessResponseSchema):
    access_token: str
    refresh_token: str


class ChangePasswordSchema(BaseModel):
    """Schema for changing password of a mod"""

    old_password: str
    new_password: str
    confirm_new_password: str


class UpdateModeratorSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    country_preferences: list[ACE] = Field(default=[])


class UpdateModeratorByAdminSchema(UpdateModeratorSchema):
    is_admin: bool | None = None


class DeactivateModeratorSchema(BaseModel):
    is_active: bool


class ReturnModeratorDataForAdmin(CreateModeratorResponseSchema):
    pending_submissions: list[str]


class RetrieveModeratorsModelResponseSchema(BaseSuccessResponseSchema):
    data: list[ReturnModeratorDataForAdmin]


class RetrieveSingleModeratorModelResponseSchema(BaseSuccessResponseSchema):
    data: ReturnModeratorDataForAdmin
