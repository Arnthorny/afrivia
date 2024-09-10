from pydantic import BaseModel


class BaseSuccessResponseSchema(BaseModel):
        success: bool
        message: str