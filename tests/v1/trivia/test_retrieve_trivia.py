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


def mock_trivia(question="Who"):
    triv = Trivia(
        id=str(uuid7()),
        question=question,
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


class TestRetrieveTrivias:

    @classmethod
    def setup_class(cls):
        app.dependency_overrides[get_db] = db_session_mock
        app.dependency_overrides[mod_service.get_current_mod] = lambda: MagicMock(
            id="mod_id"
        )

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_get_all_trivias(self, client, mocker: MockerFixture):
        """Test to verify response for getting all trivias."""

        mock_trivia_data = [
            mock_trivia(),
            mock_trivia("Who is the first?"),
        ]

        mocker.patch.object(trivia_service, "fetch_all", return_value=mock_trivia_data)
        response = client.get(ENDPOINT_URL.format(""))

        assert response.status_code == 200
        assert response.json()["data"][0]["question"] == mock_trivia_data[0].question
        assert (
            response.json()["data"][1]["difficulty"] == mock_trivia_data[1].difficulty
        )

    def test_get_all_trivias_empty(self, client, mocker: MockerFixture):
        """Test to verify response for getting all trivias, even when there are
        none."""

        mock_trivia_data = []
        mocker.patch.object(trivia_service, "fetch_all", return_value=mock_trivia_data)
        response = client.get(ENDPOINT_URL.format(""))

        assert response.status_code == 200
        assert response.json().get("data") == []

    def test_get_trivia_single(self, client, mocker):
        """Test to successfully fetch a single trivia"""

        mock_triv = mock_trivia()

        mocker.patch.object(trivia_service, "fetch", return_value=mock_triv)

        response = client.get(ENDPOINT_URL.format(mock_triv.id))

        assert response.status_code == 200
        assert response.json()["data"]["question"] == mock_triv.question
        assert response.json()["data"]["id"] == mock_triv.id

    # Invalid id
    def test_retrieve_trivia_invalid_id(self, client, mocker):
        """Test to retrieve trivia with an invalid id"""
        mocker.patch.object(mocked_db, "get", return_value=None)

        response = client.get(ENDPOINT_URL.format("invalid-id"))
        assert response.status_code == 404
        assert response.json()["message"] == "Trivia not found"

    def test_retrieve_single_trivia_unauthenticated(self, client, mocker):
        """Test to retrieve a single trivia without sign-in"""
        app.dependency_overrides = {}
        response = client.get(ENDPOINT_URL.format("id"))

        assert response.status_code == 401
        assert response.json()["message"] == "Could not validate credentials"

    def test_retrieve_all_trivias_unauthenticated(self, client, mocker):
        """Test to retrieve all trivias without sign-in"""
        app.dependency_overrides = {}
        response = client.get(ENDPOINT_URL.format(""))

        assert response.status_code == 401
        assert response.json()["message"] == "Could not validate credentials"
