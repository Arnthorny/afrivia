import pytest

from datetime import datetime, timezone
from unittest.mock import MagicMock
from pytest_mock import MockerFixture


import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid_extensions import uuid7

from api.v1.services.moderator import (
    bearer_scheme,
    mod_service,
    HTTPAuthorizationCredentials,
)
from api.db.database import get_db
from api.v1.services.trivia import trivia_service, CountryService, CategoryService
from api.v1.models.trivia import Trivia, TriviaOption
from api.v1.models.category import Category
from api.v1.models.country import Country
from main import app

ENDPOINT_URL = "/api/v1/trivias/{}"


def mock_trivia():
    triv = Trivia(
        id=str(uuid7()),
        question="Who is the first Algerian President?",
        difficulty="medium",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    triv.categories = [Category(name="Politics")]
    triv.countries = [Country(name="Algeria")]

    triv.options = [
        TriviaOption(content="Test", is_correct=False),
        TriviaOption(content="options", is_correct=False),
        TriviaOption(content="for", is_correct=False),
        TriviaOption(content="mocked data", is_correct=True),
    ]

    return triv


mocked_db = MagicMock(spec=Session)


def db_session_mock():
    yield mocked_db


@pytest.fixture
def client():
    client = TestClient(app)
    yield client


test_triv_body_1 = {
    "question": "Who was the first president of Algeria?",
    "category": "General-Knowledge",
    "countries": ["Nigeria"],
}

test_triv_update_body_2 = {
    "correct_option": "Abdelmadjid Tebboune",
}


class TestUpdateTrivia:

    @classmethod
    def setup_class(cls):
        app.dependency_overrides[get_db] = db_session_mock
        app.dependency_overrides[mod_service.get_current_admin] = lambda: MagicMock(
            id="mod_id"
        )

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_update_trivia_success(self, client, mocker: MockerFixture):
        """Test to successfully update a trivia"""

        # Mock the user service to return the current user

        mock_triv = mock_trivia()
        mocker.patch.object(trivia_service, "fetch", return_value=mock_triv)
        mocker.patch.object(
            CategoryService,
            "fetch_categories",
            return_value=[Category(name=test_triv_body_1["category"])],
        )
        mocker.patch.object(
            CountryService,
            "fetch_countries",
            return_value=[Country(name=test_triv_body_1["countries"][0])],
        )

        response = client.put(ENDPOINT_URL.format("some-id"), json=test_triv_body_1)

        assert response.status_code == 200
        assert response.json()["data"]["id"] == mock_triv.id
        assert response.json()["data"]["difficulty"] == mock_triv.difficulty

        assert response.json()["data"]["question"] == test_triv_body_1["question"]
        assert response.json()["data"]["category"] == test_triv_body_1["category"]
        assert response.json()["data"]["countries"] == test_triv_body_1["countries"]

    def test_update_trivia_correct_option_success(self, client, mocker: MockerFixture):
        """Test to successfully update a trivia"""

        # Mock the user service to return the current user

        mock_triv = mock_trivia()
        mocker.patch.object(trivia_service, "fetch", return_value=mock_triv)
        response = client.put(
            ENDPOINT_URL.format("some-id"), json=test_triv_update_body_2
        )

        assert response.status_code == 200
        assert response.json()["data"]["id"] == mock_triv.id

        assert (
            response.json()["data"]["correct_option"]
            == test_triv_update_body_2["correct_option"]
        )

    def test_update_empty_fields(self, client, mocker):
        """Test for completely empty fields when updating a trivia"""

        mock_triv = mock_trivia()

        mocker.patch.object(trivia_service, "fetch", return_value=mock_triv)
        response = client.put(ENDPOINT_URL.format("some-id"), json={})

        assert response.status_code == 200

        assert response.json()["data"]["question"] == mock_triv.question
        assert response.json()["data"]["id"] == mock_triv.id

    # Invalid id
    def test_update_trivia_invalid_id(self, client, mocker):

        mocker.patch.object(mocked_db, "get", return_value=None)

        response = client.put(ENDPOINT_URL.format("invalid-id"), json={})
        assert response.status_code == 404
        assert response.json()["message"] == "Trivia not found"

    def test_put_trivia_forbidden(self, client, mocker):
        """Test unauthourized user"""
        app.dependency_overrides = {}
        app.dependency_overrides[get_db] = lambda: mocked_db
        app.dependency_overrides[bearer_scheme] = lambda: HTTPAuthorizationCredentials(
            scheme="bearer", credentials="some-token"
        )

        mocker.patch.object(
            mod_service,
            "get_current_mod",
            return_value=MagicMock(is_admin=False),
        )
        response = client.put(ENDPOINT_URL.format("some-id"), json={})

        assert response.status_code == 403
        assert (
            response.json()["message"]
            == "You do not have permission to access this resource"
        )
