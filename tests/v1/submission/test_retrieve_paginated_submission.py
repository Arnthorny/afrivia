from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from pytest_mock import MockerFixture
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.routes.submission import mod_service
from api.v1.services.submission import submission_service
from api.v1.models.submission import Submission, SubmissionOption
from api.v1.models.category import Category
from api.v1.models.country import Country
from main import app


def mock_submission():
    return Submission(
        id=str(uuid7()),
        question="Who is the first Algerian President?",
        status="Pending",
        difficulty="easy",
        moderator_id="some_mod",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


db_session_mock = MagicMock(spec=Session)


def db_session_mock_fn():
    yield db_session_mock


client = TestClient(app)


mock_db_store = [
    {
        "question": "In what year was the African Union established?",
        "incorrect_options": ["2005", "1993", "1999"],
        "correct_option": "2001",
        "difficulty": "easy",
        "submission_note": None,
        "category": "General Knowledge",
        "countries": [],
        "id": "066dfa7d-f307-7974-8000-a3ee98a563f3",
        "status": "pending",
        "created_at": "2024-09-10T02:58:55.149655+01:00",
    },
    {
        "question": "Who is the current president of Algeria?",
        "incorrect_options": ["Lil Wayne", "George Bush", "Barack Obama"],
        "correct_option": "Abdelmadjid Tebboune",
        "difficulty": "easy",
        "submission_note": None,
        "category": "General Knowledge",
        "countries": ["Algeria"],
        "id": "066dfa4f-de25-7b53-8000-6730fbe651bf",
        "status": "pending",
        "created_at": "2024-09-10T02:46:37.863201+01:00",
    },
    {
        "question": "Whose face is present on the five hundred naira note?",
        "incorrect_options": ["Tinubu", "Kamala", "Harrison"],
        "correct_option": "Nnamdi Azikiwe",
        "difficulty": "easy",
        "submission_note": None,
        "category": "General Knowledge",
        "countries": ["Nigeria"],
        "id": "066dfa48-83c8-7c0d-8000-1857173fd0d5",
        "status": "rejected",
        "created_at": "2024-09-10T02:44:40.194681+01:00",
    },
    {
        "question": "Whose face is present on the ten naira note?",
        "incorrect_options": ["Trump", "Icheke", "Obi"],
        "correct_option": "Alvan Ikoku",
        "difficulty": "easy",
        "submission_note": None,
        "category": "General Knowledge",
        "countries": ["Nigeria"],
        "id": "066dfa22-e281-7d82-8000-b80215b771f0",
        "status": "rejected",
        "created_at": "2024-09-10T02:34:38.125340+01:00",
    },
    {
        "question": "Who is the present governor of Lagos?",
        "incorrect_options": ["Pavlov", "Durov", "Emenike"],
        "correct_option": "Sanwo Olu",
        "difficulty": "easy",
        "submission_note": None,
        "category": "General Knowledge",
        "countries": ["Nigeria"],
        "id": "066dfa0d-9d61-7748-8000-b4e4ec4bd938",
        "status": "approved",
        "created_at": "2024-09-10T02:28:57.806201+01:00",
    },
    {
        "question": "Who is the former governor of Lagos?",
        "incorrect_options": ["Pavlov", "Durov", "Emenike"],
        "correct_option": "Ambode",
        "difficulty": "easy",
        "submission_note": None,
        "category": "General Knowledge",
        "countries": ["Nigeria"],
        "id": "066dfa0a-d2e9-743d-8000-5d9a086d1d5e",
        "status": "approved",
        "created_at": "2024-09-10T02:28:13.134585+01:00",
    },
]


ENDPOINT = "/api/v1/submissions"


class TestRetrieveSubmissionForMods:

    @classmethod
    def setup_class(cls):
        app.dependency_overrides[get_db] = db_session_mock_fn
        app.dependency_overrides[mod_service.get_current_mod] = lambda: MagicMock(
            id="mod_id"
        )
        pass

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    # Retrieve all submissions for a moderator with default pagination
    def test_retrieve_all_submissions_default_pagination(self, mocker: MockerFixture):

        with patch.object(
            submission_service, "fetch_paginated", return_value=[]
        ) as mock_obj:

            response = client.get(ENDPOINT)
            assert response.status_code == 200
            mock_obj.assert_called_once_with(
                db=db_session_mock,
                skip=0,
                limit=5,
                filters={"moderator_id": "mod_id", "status": None},
            )
