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
    "", response_model=t_schema.GetTriviaForModResponseModelSchema, status_code=201
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
        data=jsonable_encoder(
            t_schema.RetrieveTriviaForModSchema.model_validate(t_dict)
        ),
        message="Successfully added trivia",
        status_code=201,
    )


@trivias.get(
    "/{id}", response_model=t_schema.GetTriviaForModResponseModelSchema, status_code=200
)
async def retrieve_single_trivia(
    id: str,
    db: Session = Depends(get_db),
    mod: Moderator = Depends(mod_service.get_current_mod),
):
    """Endpoint to retrieve a single trivia.

    Args:
        db (Session, optional): The db session object.
    """
    trivia = trivia_service.fetch(db=db, id=id, raise_404=True)

    t_dict = trivia.to_dict()

    return success_response(
        data=jsonable_encoder(
            t_schema.RetrieveTriviaForModSchema.model_validate(t_dict)
        ),
        message="Successfully retrieved trivia",
        status_code=200,
    )


@trivias.get(
    "",
    response_model=t_schema.GetListOfTriviaForModResponseModelSchema,
    status_code=200,
)
async def retrieve_all_trivias(
    db: Session = Depends(get_db),
    mod: Moderator = Depends(mod_service.get_current_mod),
):
    """Endpoint to retrieve all trivias.

    Args:
        db (Session, optional): The db session object.
    """
    trivias = trivia_service.fetch_all(db)

    validated_t_dict = [
        t_schema.RetrieveTriviaForModSchema.model_validate(t.to_dict()) for t in trivias
    ]

    return success_response(
        data=jsonable_encoder(validated_t_dict),
        message="Successfully retrieved all trivias",
        status_code=200,
    )


@trivias.put(
    "/{id}", response_model=t_schema.GetTriviaForModResponseModelSchema, status_code=200
)
async def update_trivia(
    id: str,
    schema: t_schema.UpdateTriviaSchema,
    db: Session = Depends(get_db),
    mod: Moderator = Depends(mod_service.get_current_admin),
):
    """Endpoint to Update a trivia.

    Args:
        schema (UpdateTriviaSchema): Request Body for updating trivia
        db (Session, optional): The db session object. Defaults to Depends(get_db).

    Returns:
    """
    trivia = trivia_service.update(db=db, schema=schema, id=id)
    t_dict = trivia.to_dict()

    logger.info(f"Updated Trivia. ID: {trivia.id}.")
    return success_response(
        data=jsonable_encoder(
            t_schema.RetrieveTriviaForModSchema.model_validate(t_dict)
        ),
        message="Successfully updated trivia",
        status_code=200,
    )


@trivias.delete(
    "/{id}",
    status_code=204,
)
async def delete_single_trivia(
    id: str,
    db: Session = Depends(get_db),
    mod: Moderator = Depends(mod_service.get_current_admin),
):
    """Endpoint to delete a single trivia.

    Args:
        db (Session, optional): The db session object.
    """
    status = trivia_service.delete(db=db, id=id)
    print(status)
