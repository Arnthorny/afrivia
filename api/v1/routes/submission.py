from fastapi import APIRouter, Depends, status, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Annotated, Literal

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.schemas.submission import (
    CreateSubmissionSchema,
    PostSubmissionResponseSchema,
    PostSubmissionResponseModelSchema,
    PaginatedResponseModelSchema,
)
from api.v1.services.moderator import mod_service, Moderator
from api.v1.services.submission import submission_service
from api.utils.logger import logger
from api.utils import responses

assigned_submissions = APIRouter(prefix="/assigned-submissions", tags=["Submissions"])
submissions = APIRouter(prefix="/submissions", tags=["Submissions"])


@submissions.post("", response_model=PostSubmissionResponseModelSchema, status_code=201)
async def create_submission(
    schema: CreateSubmissionSchema, db: Session = Depends(get_db)
):
    """Endpoint to create a new submission.

    Args:
        schema (CreateSubmissionSchema): Request Body for creating submission
        db (Session, optional): The db session object. Defaults to Depends(get_db).

    Returns:
    """
    submission = submission_service.create(db, schema=schema)
    s_dict = submission.to_dict()

    logger.info(f"Created new submission. ID: {submission.id}.")
    return success_response(
        data=jsonable_encoder(PostSubmissionResponseSchema.model_validate(s_dict)),
        message="Successfully added submission",
        status_code=status.HTTP_201_CREATED,
    )


@assigned_submissions.get(
    "", response_model=PaginatedResponseModelSchema, status_code=200
)
async def retrieve_submission_for_mods(
    status: Literal["pending", "approved", "rejected"] | None = None,
    page: Annotated[int | None, Query(gt=0)] = 1,
    limit: Annotated[int | None, Query(gt=0)] = 5,
    db: Session = Depends(get_db),
    current_mod: Moderator = Depends(mod_service.get_current_mod),
):
    """Endpoint to retrieves submissions assigned to a particular moderator\n

    Args:\n
        status (Literal['pending', 'approved', 'rejected'] | None, optional): The kind of submissions to be retrieved. If None, retrieve all submissions. Defaults to None.\n
        page (Annotated[int  |  None, Query, optional): The page to be retrieved. Defaults to 0)]=1.\n
        limit (Annotated[int  |  None, Query, optional): The number of items per page. Defaults to 0)]=5.\n
        db (Session): The db session.\n
        current_mod (Moderator): Mod making the request.
    """
    filter_obj = {"moderator_id": current_mod.id, "status": status}

    # Naturally page numbers start from 1. On the db we calculate skip(items to skip over) from 0
    skip = (page - 1) * limit

    paged_res = submission_service.fetch_paginated(
        db=db, skip=skip, limit=limit, filters=filter_obj
    )

    return success_response(
        status_code=200, message="Submissions retrieved successfully", data=paged_res
    )
