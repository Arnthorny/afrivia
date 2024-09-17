from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.schemas.moderator import (
    CreateModeratorResponseSchema,
    GetModeratorResponseModelSchema,
    ChangePasswordSchema,
    RetrieveModeratorsModelResponseSchema,
    ReturnModeratorDataForAdmin,
)
from api.v1.services.moderator import mod_service, Moderator
from api.utils.logger import logger

moderator = APIRouter(prefix="/moderators", tags=["Moderators"])


@moderator.get("/me", response_model=GetModeratorResponseModelSchema, status_code=200)
async def get_same_moderator(
    db: Session = Depends(get_db),
    current_mod: Moderator = Depends(mod_service.get_current_mod),
):
    """Endpoint to get a moderator's detail.

    Args:
        db (Session, optional): The db session object. Defaults to Depends(get_db).

    Returns:
    """
    mod_dict = current_mod.to_dict()

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Moderator successfully retrieved",
        data=jsonable_encoder(CreateModeratorResponseSchema.model_validate(mod_dict)),
    )


@moderator.patch(
    "/update/password", status_code=status.HTTP_200_OK, response_model=success_response
)
def change_password(
    schema: ChangePasswordSchema,
    db: Session = Depends(get_db),
    current_mod: Moderator = Depends(mod_service.get_current_mod),
):
    """Route to change the user's password"""

    mod_service.change_password(user=current_mod, db=db, **schema.model_dump())

    logger.info(f"Changed password for Mod with id={current_mod.id}")

    return success_response(
        status_code=status.HTTP_200_OK, message="Password changed successfully!!"
    )


@moderator.get(
    "",
    response_model=RetrieveModeratorsModelResponseSchema,
    status_code=200,
)
async def retrieve_all_moderators(
    db: Session = Depends(get_db),
    mod: Moderator = Depends(mod_service.get_current_admin),
):
    """Endpoint to retrieve all moderators.

    Args:
        db (Session, optional): The db session object.
        mod (Moderator): The admin making the request.
    """
    mods = mod_service.fetch_all(db=db)

    validated_m_dict = [
        ReturnModeratorDataForAdmin.model_validate(m.to_dict()) for m in mods
    ]

    return success_response(
        data=jsonable_encoder(validated_m_dict),
        message="Successfully retrieved all moderators",
        status_code=200,
    )


@moderator.patch(
    "/{id}/activate",
    response_model=GetModeratorResponseModelSchema,
    status_code=200,
)
async def activate_moderator(
    id: str,
    db: Session = Depends(get_db),
    current_mod: Moderator = Depends(mod_service.get_current_admin),
):
    """Endpoint for admin to activate a deactivated moderator's account"""

    mod = mod_service.deactivateOrActivate(
        db=db, id_target=id, current_mod=current_mod, is_active=True
    )

    return success_response(
        status_code=200,
        message=f"Moderator successfully activated",
        data=CreateModeratorResponseSchema.model_validate(mod.to_dict()),
    )


@moderator.patch(
    "/{id}/deactivate",
    response_model=GetModeratorResponseModelSchema,
    status_code=200,
)
async def deactivate_moderator(
    id: str,
    db: Session = Depends(get_db),
    current_mod: Moderator = Depends(mod_service.get_current_mod),
):
    """Endpoint for admin or a mod to deactivate a moderator's account
    Regular mods can only deactivate their own account
    """

    mod = mod_service.deactivateOrActivate(
        db=db, id_target=id, current_mod=current_mod, is_active=False
    )

    return success_response(
        status_code=200,
        message=f"Moderator successfully deactivated",
        data=CreateModeratorResponseSchema.model_validate(mod.to_dict()),
    )


@moderator.delete(
    "/{id}",
    status_code=204,
)
async def delete_single_moderator(
    id: str,
    db: Session = Depends(get_db),
    mod: Moderator = Depends(mod_service.get_current_admin),
):
    """Endpoint to delete a single moderator.

    Args:
        db (Session, optional): The db session object.
    """
    status = mod_service.delete(db=db, id_target=id, current_admin=mod)
