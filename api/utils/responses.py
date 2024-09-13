from pydantic import BaseModel


class BaseErrResponseModel(BaseModel):
    success: bool = False
    message: str


class Regular401Response(BaseErrResponseModel):
    status_code: int = 401


class Regular500Response(BaseErrResponseModel):
    status_code: int = 500
