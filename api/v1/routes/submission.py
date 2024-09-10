
from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.schemas.submission import CreateSubmissionSchema, PostSubmissionResponseSchema, PostSubmissionResponseModelSchema
from api.v1.services.submission import submission_service
from api.utils.logger import logger

submissions = APIRouter(prefix='/submissions', tags=['Submissions'])

@submissions.post("",
                  response_model=PostSubmissionResponseModelSchema,
                  status_code=201)
async def create_submission(
    schema: CreateSubmissionSchema,
    db: Session = Depends(get_db)
    ):
    """Endpoint to create a new submission.

    Args:
        schema (CreateSubmissionSchema): Request Body for creating submission
        db (Session, optional): The db session object. Defaults to Depends(get_db).

    Returns:
    """
    submission = submission_service.create(db, schema=schema)
    s_dict = submission.to_dict()
    
    logger.info(f'Created new submission. ID: {submission.id}.')
    return success_response(
        data=jsonable_encoder(PostSubmissionResponseSchema.model_validate(s_dict)),
        message="Successfully added submission",
        status_code=status.HTTP_201_CREATED,
    )