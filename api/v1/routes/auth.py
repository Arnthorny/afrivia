from datetime import timedelta
from fastapi import (
    Depends,
    status,
    APIRouter,
    Response,
    Request,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from api.v1.models.moderator import Moderator

from api.utils.success_response import success_response

from api.v1.schemas.moderator import (
    ModeratorLoginSchema,
    CreateModeratorSchema,
    CreateModeratorResponseSchema,
    CreateModeratorResponseModelSchema,
    RefreshAccessTokenResponse,
    ModeratorLogoutResponse,
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
    schema: CreateModeratorSchema,
    db: Session = Depends(get_db),
):
    """Endpoint for a mod to register their account"""

    # Create mod account
    mod = mod_service.create(db=db, schema=schema)

    # Create access and refresh tokens
    access_token = mod_service.create_access_token(mod_id=mod.id)
    refresh_token = mod_service.create_refresh_token(mod_id=mod.id)

    # TODO Send welcome email in the background
    # email_sending_service.send_welcome_email(request, background_tasks, mod)

    mod_dict = mod.to_dict()

    response = JSONResponse(
        status_code=201,
        content={
            "success": True,
            "message": "Moderator created successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "data": jsonable_encoder(
                CreateModeratorResponseSchema.model_validate(mod_dict)
            ),
        },
    )

    # Add refresh token to session cookies
    request.session["refresh_token"] = refresh_token
    # response.set_cookie(
    #     key="refresh_token",
    #     value=refresh_token,
    #     expires=timedelta(days=60),
    #     httponly=True,
    #     secure=True,
    #     samesite="none",
    # )

    return response


@auth.post(
    path="/register-admin",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateModeratorResponseModelSchema,
)
def register_as_admin(
    request: Request,
    schema: CreateModeratorSchema,
    db: Session = Depends(get_db),
):
    """Endpoint to register an admin account"""

    # Create mod account
    mod = mod_service.create(db=db, schema=schema, is_admin=True)

    # Create access and refresh tokens
    access_token = mod_service.create_access_token(mod_id=mod.id)
    refresh_token = mod_service.create_refresh_token(mod_id=mod.id)

    # TODO Send welcome email in the background
    # email_sending_service.send_welcome_email(request, background_tasks, mod)

    mod_dict = mod.to_dict()

    response = JSONResponse(
        status_code=201,
        content={
            "success": True,
            "message": "Admin created successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "data": jsonable_encoder(
                CreateModeratorResponseSchema.model_validate(mod_dict)
            ),
        },
    )

    # Add refresh token to session cookies
    request.session["refresh_token"] = refresh_token

    return response


@auth.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=CreateModeratorResponseModelSchema,
)
def login(
    login_schema: ModeratorLoginSchema, request: Request, db: Session = Depends(get_db)
):
    """Endpoint to log in a mod"""

    # Authenticate the mod
    mod = mod_service.authenticate_mod(
        db=db, email=login_schema.email, password=login_schema.password
    )

    # Generate access and refresh tokens
    access_token = mod_service.create_access_token(mod_id=mod.id)
    refresh_token = mod_service.create_refresh_token(mod_id=mod.id)

    mod_dict = mod.to_dict()

    response = JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "data": jsonable_encoder(
                CreateModeratorResponseSchema.model_validate(mod_dict)
            ),
        },
    )

    # Add refresh token to session cookies
    request.session["refresh_token"] = refresh_token
    return response


@auth.post(
    "/logout", status_code=status.HTTP_200_OK, response_model=ModeratorLogoutResponse
)
def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_mod: Moderator = Depends(mod_service.get_current_mod),
):
    """Endpoint to log a mod out of their account"""

    # Delete refresh token from cookies
    request.session.pop("refresh_token", None)

    return success_response(
        status_code=200, message="Moderator logged out successfully"
    )


@auth.post(
    "/refresh-access-token",
    status_code=status.HTTP_200_OK,
    response_model=RefreshAccessTokenResponse,
)
def refresh_access_token(request: Request, db: Session = Depends(get_db)):
    """Endpoint to refresh a mod's access token"""

    # Get refresh token
    current_refresh_token = request.session.get("refresh_token", None)

    # Create new access and refresh tokens
    access_token, refresh_token = mod_service.refresh_access_token(
        current_refresh_token=current_refresh_token
    )

    response = JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Token refreshed successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
    )

    return response
