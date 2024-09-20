from typing import Optional
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response(status_code: int, message: str, data: Optional[dict] = None):
    """Returns a JSON response for success responses"""

    response_data = {"success": True, "message": message}

    if data is not None:
        response_data["data"] = data

    return JSONResponse(
        status_code=status_code, content=jsonable_encoder(response_data)
    )


def failure_response(status_code: int, message: str, data: Optional[dict] = None):
    """Returns a JSON response for failure responses"""

    response_data = {"success": False, "message": message, "data": None}

    return JSONResponse(
        status_code=status_code, content=jsonable_encoder(response_data)
    )
