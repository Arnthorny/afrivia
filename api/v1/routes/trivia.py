from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.schemas import trivia as t_schema

from api.v1.services.moderator import mod_service, Moderator
from api.v1.services.trivia import trivia_service
from api.utils.logger import logger

trivias = APIRouter(prefix="/trivias", tags=["Trivias"])


@trivias.post(
    "", response_model=t_schema.PostTriviaResponseModelSchema, status_code=201
)
async def create_trivia(
    schema: t_schema.CreateTriviaSchema,
    db: Session = Depends(get_db),
    mod: Moderator = Depends(mod_service.get_current_mod),
):
    """Endpoint to create a new trivia.

    Args:
        schema (CreateTriviaSchema): Request Body for creating trivia
        db (Session, optional): The db session object. Defaults to Depends(get_db).

    Returns:
    """
    trivia = trivia_service.create(db, schema=schema)
    t_dict = trivia.to_dict()

    logger.info(f"Created new Trivia. ID: {trivia.id}.")
    return success_response(
        data=jsonable_encoder(t_schema.PostTriviaResponseSchema.model_validate(t_dict)),
        message="Successfully added trivia",
        status_code=201,
    )
