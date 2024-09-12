from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.schemas.moderator import (
    CreateModeratorResponseSchema,
    GetModeratorResponseModelSchema,
    ChangePasswordSchema,
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
