from datetime import timedelta
from fastapi import (
    Depends,
    status,
    APIRouter,
    Response,
    Request,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.utils.success_response import success_response
from api.v1.models import User

from api.v1.schemas.moderator import (
    ModeratorLoginSchema,
    CreateModeratorSchema,
    CreateModeratorResponseModelSchema,
    RegisterUserResponse,
    RefreshAccessTokenResponse,
    LogoutResponse,
    MagicLinkResponse,
)

from api.db.database import get_db
from api.v1.services.moderator import mod_service


auth = APIRouter(prefix="/auth", tags=["Authentication"])


@auth.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateModeratorResponseModelSchema,
)
def register(
    request: Request,
    response: Response,
    schema: CreateModeratorSchema,
    db: Session = Depends(get_db),
):
    """Endpoint for a user to register their account"""

    # Create mod account
    mod = mod_service.create(db=db, schema=schema)

    # Create access and refresh tokens
    access_token = mod_service.create_access_token(user_id=mod.id)
    refresh_token = mod_service.create_refresh_token(user_id=mod.id)

    #TODO Send welcome email in the background
    # email_sending_service.send_welcome_email(request, background_tasks, user)

    response = JSONResponse(
        status_code=201,
        content={
            "status_code": 201,
            "message": "User created successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "data": {
                "user": jsonable_encoder(
                    user, exclude=["password", "is_deleted", "updated_at"]
                ),
                "user_subscription": jsonable_encoder(
                    user_subscription, exclude=["user_id"]
                ),
            },
        },
    )

    # Add refresh token to cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=60),
        httponly=True,
        secure=True,
        samesite="none",
    )

    return response


@auth.post(
    path="/register-super-admin",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterUserResponse,
)
@limiter.limit("20/minute")  # Limit to 20 requests per minute per IP
def register_as_super_admin(
    user: UserCreate, request: Request, db: Session = Depends(get_db)
):
    """Endpoint for super admin creation"""

    user = user_service.create_admin(db=db, schema=user)

    # Create access and refresh tokens
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    response = JSONResponse(
        status_code=201,
        content={
            "status_code": 201,
            "message": "User created successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "data": {
                "user": jsonable_encoder(
                    user, exclude=["password", "is_deleted", "updated_at"]
                )
            },
        },
    )

    # Add refresh token to cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=60),
        httponly=True,
        secure=True,
        samesite="none",
    )

    return response


@auth.post(
    "/login", status_code=status.HTTP_200_OK, response_model=RegisterUserResponse
)
@limiter.limit("20/minute")  # Limit to 20 requests per minute per IP
def login(login_request: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Endpoint to log in a user"""

    # Authenticate the user
    user = user_service.authenticate_user(
        db=db, email=login_request.email, password=login_request.password
    )

    # Generate access and refresh tokens
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    response = JSONResponse(
        status_code=200,
        content={
            "status_code": 200,
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "data": {
                "user": jsonable_encoder(
                    user, exclude=["password", "is_deleted", "updated_at"]
                )
            },
        },
    )

    # Add refresh token to cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=30),
        httponly=True,
        secure=True,
        samesite="none",
    )

    return response


@auth.post("/logout", status_code=status.HTTP_200_OK, response_model=LogoutResponse)
def logout(
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to log a user out of their account"""

    response = success_response(status_code=200, message="User logged put successfully")

    # Delete refresh token from cookies
    response.delete_cookie(key="refresh_token")

    return response


@auth.post(
    "/refresh-access-token",
    status_code=status.HTTP_200_OK,
    response_model=RefreshAccessTokenResponse,
)
@limiter.limit("20/minute")  # Limit to 20 requests per minute per IP
def refresh_access_token(
    request: Request, response: Response, db: Session = Depends(get_db)
):
    """Endpoint to log a user out of their account"""

    # Get refresh token
    current_refresh_token = request.cookies.get("refresh_token")

    # Create new access and refresh tokens
    access_token, refresh_token = user_service.refresh_access_token(
        current_refresh_token=current_refresh_token
    )

    response = response = JSONResponse(
        status_code=200,
        content={
            "status_code": 200,
            "message": "Tokens refreshed successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
    )

    # Add refresh token to cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=30),
        httponly=True,
        secure=True,
        samesite="none",
    )

    return response
