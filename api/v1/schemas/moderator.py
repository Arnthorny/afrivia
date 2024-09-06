from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class ModeratorBaseSchema(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    username: str = Field(min_length=1)
    email: EmailStr
    country_preferences: None | list[str] = Field(min_length=1, default=[])

class CreateModeratorSchema(ModeratorBaseSchema):
    password: str = Field(min_length=1)


class ModeratorResponseSchema(ModeratorBaseSchema):
    id: str
    updated_at: datetime
    is_admin: bool
    is_active: bool
    class Config:
        from_attributes = True


class UpdateModeratorSchema(BaseModel):
    first_name: str | None = None
    last_name: str  | None = None
    username: str  | None = None
    password: str  | None = None
    country_preferences: None | list[str] = Field(min_length=1, default=[])


class UpdateModeratorByAdminSchema(UpdateModeratorSchema):
    is_admin: bool | None = None

class DeactivateModeratorSchema(BaseModel):
    is_active: bool