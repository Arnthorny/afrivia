import pytest
from api.v1.schemas.submission import CreateSubmissionSchema
from api.v1.routes.submission import create_submission

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.services.moderator import mod_service
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


def db_session_mock():
    db_session = MagicMock(spec=Session)
    yield db_session


client = TestClient(app)


test_sub_req_body_1 = {
    "question": "Who is the current president of Algeria?",
    "incorrect_options": ["Lil Wayne", "George Bush", "Barack Obama"],
    "correct_option": "Abdelmadjid Tebboune",
    "difficulty": "easy",
    "category": "General Knowledge",
    "countries": ["Algeria"],
}


class TestCreateSubmission:

    @classmethod
    def setup_class(cls):
        app.dependency_overrides[get_db] = db_session_mock

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_create_submission_success(self, mocker):
        """Test to successfully create a new submission"""
        test_body_copy = test_sub_req_body_1.copy()

        def mock_extractor(dump, db):
            # Mock the extractor method and inject/remove values to/from the schema dump
            all_options = test_body_copy.get("incorrect_options").copy()
            all_options.append(test_body_copy.get("correct_option"))

            dump.pop("incorrect_options")
            dump.pop("correct_option")
            dump.pop("countries")
            dump.pop("category")

            dump["id"] = "dummy_id"
            dump["status"] = "pending"
            dump["created_at"] = datetime.now()
            dump["updated_at"] = datetime.now()

            return [
                [Country(name="Algeria")],
                [Category(name="General Knowledge")],
                [
                    SubmissionOption(content=all_options[0]),
                    SubmissionOption(content=all_options[1]),
                    SubmissionOption(content=all_options[2]),
                    SubmissionOption(content=all_options[3], is_correct=True),
                ],
            ]

        mocker.patch.object(
            submission_service, "extract_countries_categories_options", mock_extractor
        )

        mocker.patch.object(
            submission_service, "find_suitable_mod", return_value="some_mod"
        )

        response = client.post("/api/v1/submissions", json=test_body_copy)

        assert response.status_code == 201
        assert response.json()["data"]["question"] == test_sub_req_body_1["question"]
        assert response.json()["data"]["category"] == test_sub_req_body_1["category"]
        assert response.json()["data"]["countries"] == test_sub_req_body_1["countries"]

    def test_create_submission_duplicate(self, mocker):
        """Test for creating duplicate submissions"""
        test_body_copy = test_sub_req_body_1.copy()
        mock_sub = mock_submission()
        db_store = []

        def mock_create(db, schema):
            # Mock the create method
            if mock_sub in db_store:
                raise IntegrityError(None, None, None)
            db_store.append(mock_sub)
            return mocker.Mock()

        mocker.patch.object(submission_service, "create", mock_create)
        mocker.patch(
            "api.v1.schemas.submission.PostSubmissionResponseSchema",
            return_value=mocker.Mock(),
        )

        response = client.post("/api/v1/submissions", json=test_body_copy)
        assert response.status_code == 201

        with pytest.raises(IntegrityError) as exc:
            response = client.post("/api/v1/submissions", json=test_body_copy)
            assert response.status_code == 400
            assert response.json()["message"] == "This question already exists"

    def test_create_submission_missing_data(self, mocker):
        """Test to unsuccessfully create a new submission"""
        test_body_copy = test_sub_req_body_1.copy()
        test_body_copy.pop("question")

        response = client.post("/api/v1/submissions", json=test_body_copy)

        assert response.status_code == 422

    def test_create_submission_malformed_data(self, mocker):
        """Test to unsuccessfully create a new submission"""
        test_body_copy = {
            "question": "?",
            "incorrect_options": ["Lil Wayne", "George Bush", "Barack Obama"],
            "correct_option": "Abdelmadjid Tebboune",
            "difficulty": "not that bad",  # Should be a member of an enum
            "category": "General Knowledge",
            "countries": "Algeria",  # Should be a list of countries
        }

        response = client.post("/api/v1/submissions", json=test_body_copy)

        assert response.status_code == 422
