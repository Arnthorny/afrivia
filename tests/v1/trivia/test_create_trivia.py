import pytest

from datetime import datetime, timezone
from unittest.mock import MagicMock
from pytest_mock import MockerFixture

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.services.moderator import mod_service
from api.v1.services.trivia import trivia_service
from api.v1.models.trivia import Trivia, TriviaOption
from api.v1.models.category import Category
from api.v1.models.country import Country
from main import app

ENDPOINT_URL = "/api/v1/trivias"


def mock_trivia():
    return Trivia(
        id=str(uuid7()),
        question="Who is the first Algerian President?",
        difficulty="easy",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def db_session_mock():
    db_session = MagicMock(spec=Session)
    yield db_session


client = TestClient(app)


test_triv_req_body_1 = {
    "question": "Who is the current president of Algeria?",
    "incorrect_options": ["Lil Wayne", "George Bush", "Barack Obama"],
    "correct_option": "Abdelmadjid Tebboune",
    "difficulty": "easy",
    "category": "General-Knowledge",
    "countries": ["Algeria"],
}


class TestCreateTrivia:

    @classmethod
    def setup_class(cls):
        app.dependency_overrides[get_db] = db_session_mock
        app.dependency_overrides[mod_service.get_current_mod] = lambda: MagicMock(
            id="mod_id"
        )

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_create_trivia_success(self, mocker):
        """Test to successfully create a new Trivia"""
        test_body_copy = test_triv_req_body_1.copy()

        def mock_extractor(dump, db):
            # Mock the extractor method and inject/remove values to/from the schema dump
            all_options = test_body_copy.get("incorrect_options").copy()
            all_options.append(test_body_copy.get("correct_option"))

            dump.pop("incorrect_options")
            dump.pop("correct_option")
            dump.pop("countries")
            dump.pop("category")

            dump["id"] = "dummy_id"
            dump["created_at"] = datetime.now()
            dump["updated_at"] = datetime.now()

            return [
                [Country(name="Algeria")],
                [Category(name="General-Knowledge")],
                [
                    TriviaOption(content=all_options[0]),
                    TriviaOption(content=all_options[1]),
                    TriviaOption(content=all_options[2]),
                    TriviaOption(content=all_options[3], is_correct=True),
                ],
            ]

        mocker.patch.object(
            trivia_service, "extract_countries_categories_options", mock_extractor
        )

        response = client.post(ENDPOINT_URL, json=test_body_copy)

        assert response.status_code == 201
        assert response.json()["data"]["question"] == test_triv_req_body_1["question"]
        assert response.json()["data"]["category"] == test_triv_req_body_1["category"]
        assert response.json()["data"]["countries"] == test_triv_req_body_1["countries"]

    def test_create_trivia_duplicate(self, mocker):
        """Test for creating duplicate trivias"""
        test_body_copy = test_triv_req_body_1.copy()
        mock_triv = mock_trivia()
        db_store = []

        def mock_create(db, schema):
            # Mock the create method
            if mock_triv in db_store:
                raise IntegrityError(None, None, None)
            db_store.append(mock_triv)
            return mocker.Mock()

        mocker.patch.object(trivia_service, "create", mock_create)
        mocker.patch(
            "api.v1.schemas.trivia.RetrieveTriviaForModSchema",
            return_value=mocker.Mock(),
        )

        response = client.post(ENDPOINT_URL, json=test_body_copy)
        assert response.status_code == 201

        with pytest.raises(IntegrityError) as exc:
            response = client.post(ENDPOINT_URL, json=test_body_copy)
            assert response.status_code == 400
            assert response.json()["message"] == "This question already exists"

    def test_create_trivia_missing_data(self, mocker):
        """Test to unsuccessfully create a new trivia"""
        test_body_copy = test_triv_req_body_1.copy()
        test_body_copy.pop("question")

        response = client.post(ENDPOINT_URL, json=test_body_copy)
        assert response.status_code == 422

    def test_create_trivia_malformed_data(self, mocker):
        """Test to unsuccessfully create a new trivia"""
        test_body_copy = {
            "question": "",
            "incorrect_options": ["Lil Wayne", "George Bush", "Barack Obama"],
            "correct_option": "Abdelmadjid Tebboune",
            "category": "General-Knowledge",
            "countries": "Algeria",  # Should be a list of countries
        }

        response = client.post(ENDPOINT_URL, json=test_body_copy)

        assert response.status_code == 422

    def test_create_trivia_unauthenticated(self, mocker):
        """Test to create a new trivia without sign-in"""
        app.dependency_overrides = {}
        response = client.post(ENDPOINT_URL, json=test_triv_req_body_1)

        assert response.status_code == 401
        assert response.json()["message"] == "Could not validate credentials"
