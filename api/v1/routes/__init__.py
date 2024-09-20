from fastapi import APIRouter
from api.v1.routes.submission import submissions, assigned_submissions
from api.v1.routes.auth import auth
from api.v1.routes.moderator import moderator
from api.v1.routes.trivia import trivias, questions

api_version_one = APIRouter(prefix="/api/v1")

api_version_one.include_router(submissions)
api_version_one.include_router(assigned_submissions)
api_version_one.include_router(auth)
api_version_one.include_router(moderator)
api_version_one.include_router(trivias)
api_version_one.include_router(questions)
