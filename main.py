import uvicorn
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import (
    SessionMiddleware,
)  # required for refresh token

# from api.utils.logger import logger
from api.utils.success_response import success_response
from api.v1.routes import api_version_one
from api.utils.settings import settings


app = FastAPI(title="Afrivia API")

https_only = settings.PYTHON_ENV == "prod"

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="lax",
    https_only=https_only,
    max_age=settings.JWT_REFRESH_EXPIRY * 24 * 60 * 60,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routes_with_credentials = [
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/register-admin",
    "/api/v1/auth/refresh-token"
    "/api/v1/auth/logout"
]

# Apply CORS middleware to specific routes
@app.middleware("http")
async def cors_middleware(request, call_next):
    response = await call_next(request)

    # Check the request path and apply CORS middleware accordingly
    if request.url.path in routes_with_credentials:
        response.headers["Access-Control-Allow-Origin"] = settings.APP_URL

    return response


app.include_router(api_version_one)


# REGISTER EXCEPTION HANDLERS
@app.exception_handler(HTTPException)
async def http_exception(request: Request, exc: HTTPException):
    """HTTP exception handler"""

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "message": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception(request: Request, exc: RequestValidationError):
    """Validation exception handler"""

    # errors = [
    #     {"loc": error["loc"], "msg": error["msg"], "type": error["type"]}
    #     for error in exc.errors()
    # ]

    errors = list(exc.errors())

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "status_code": 422,
            "message": "Invalid input",
            "errors": errors,
        },
    )


@app.exception_handler(Exception)
async def exception(request: Request, exc: Exception):
    """Other exception handlers"""

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "status_code": 500,
            "message": f"An unexpected error occurred. Check the logs.",
        },
    )


@app.get("/", tags=["Home"], status_code=status.HTTP_200_OK)
async def get_root(request: Request) -> dict:
    return success_response(
        status_code=200,
        message="Welcome to Afrivia API",
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        port=7001,
        reload=True,
        workers=4,
    )
