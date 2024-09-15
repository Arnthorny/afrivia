from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Annotated, Literal

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.schemas import submission as s_schema

from api.v1.services.moderator import mod_service, Moderator
from api.v1.services.submission import submission_service
from api.utils.logger import logger
from api.utils import responses

assigned_submissions = APIRouter(prefix="/assigned-submissions", tags=["Submissions"])
submissions = APIRouter(prefix="/submissions", tags=["Submissions"])


@submissions.post(
    "", response_model=s_schema.PostSubmissionResponseModelSchema, status_code=201
)
async def create_submission(
    schema: s_schema.CreateSubmissionSchema, db: Session = Depends(get_db)
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
        data=jsonable_encoder(
            s_schema.PostSubmissionResponseSchema.model_validate(s_dict)
        ),
        message="Successfully added submission",
        status_code=201,
    )


@assigned_submissions.get(
    "", response_model=s_schema.PaginatedResponseModelSchema, status_code=200
)
async def retrieve_submissions_for_mods(
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


@assigned_submissions.get(
    "/{id}",
    response_model=s_schema.GetSubmissionForModResponseModelSchema,
    status_code=200,
)
async def retrieve_single_submission_for_mods(
    id: str,
    db: Session = Depends(get_db),
    current_mod: Moderator = Depends(mod_service.get_current_mod),
):
    """Endpoint to retrieve single submission assigned to a particular moderator\n

    Args:\n
        id (str): The id of submission to be retrieved.\n
        db (Session): The db session.\n
        current_mod (Moderator): Mod making the request.
    """

    subm = submission_service.fetch_assigned_submission(
        db=db, mod_id=current_mod.id, target_id=id
    )

    return success_response(
        status_code=200,
        message="Submissions retrieved successfully",
        data=s_schema.RetrieveSubmissionForModSchema.model_validate(subm.to_dict()),
    )


@assigned_submissions.patch(
    "/{id}/review",
    response_model=s_schema.GetSubmissionForModResponseModelSchema,
    status_code=200,
)
async def approve_single_submission(
    id: str,
    status: Literal["approved", "rejected"],
    db: Session = Depends(get_db),
    current_mod: Moderator = Depends(mod_service.get_current_mod),
):
    """Endpoint to approve/reject single submission assigned to a particular moderator\n

    Args:\n
        id (str): The id of submission to be retrieved.\n
        review_status (str): query parameter for use in reviewing.\n
        db (Session): The db session.\n
        current_mod (Moderator): Mod making the request.
    """

    subm = submission_service.review_assigned_submission(
        db=db, mod_id=current_mod.id, target_id=id, review_status=status
    )

    return success_response(
        status_code=200,
        message=f"Submission marked as {status}",
        data=s_schema.RetrieveSubmissionForModSchema.model_validate(subm.to_dict()),
    )
