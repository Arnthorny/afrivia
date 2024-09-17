import pytest

from datetime import datetime, timezone
from unittest.mock import MagicMock
from pytest_mock import MockerFixture


import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid_extensions import uuid7

from api.v1.services.moderator import mod_service
from api.db.database import get_db
from api.v1.services.trivia import trivia_service, CountryService, CategoryService
from api.v1.services.submission import submission_service
from api.v1.models.trivia import Trivia, TriviaOption
from api.v1.models.category import Category
from api.v1.models.country import Country
from main import app

ENDPOINT_URL = "/api/v1/submissions/{}/similars"


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


class TestRetrieveSimilarTriviasToSubmission:

    @classmethod
    def setup_class(cls):
        app.dependency_overrides[get_db] = db_session_mock
        app.dependency_overrides[mod_service.get_current_mod] = lambda: MagicMock(
            id="mod_id"
        )

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_get_all_similar_trivias(self, client, mocker: MockerFixture):
        """Test to verify response for getting all similar trivias."""

        mock_trivia_data = [
            mock_trivia(),
            mock_trivia("Who is the first?"),
        ]

        mock_obj = mocker.patch.object(
            submission_service, "fetch_similars", return_value=mock_trivia_data
        )

        id = "some-id"
        response = client.get(ENDPOINT_URL.format(id))

        assert response.status_code == 200
        mock_obj.assert_called_once_with(db=mocked_db, id=id)

        assert response.status_code == 200
        assert response.json()["data"][0]["question"] == mock_trivia_data[0].question
        assert (
            response.json()["data"][1]["difficulty"] == mock_trivia_data[1].difficulty
        )

    def test_get_all_similar_trivias_empty(self, client, mocker: MockerFixture):
        """Test to verify response for getting  similar trivias, even when there are none."""

        mock_trivia_data = []
        mock_obj = mocker.patch.object(
            submission_service, "fetch_similars", return_value=mock_trivia_data
        )
        id = "some-id"
        response = client.get(ENDPOINT_URL.format(id))
        mock_obj.assert_called_once_with(db=mocked_db, id=id)

        assert response.status_code == 200
        assert response.json().get("data") == []

    def test_retrieve_all_similar_trivias_unauthenticated(self, client, mocker):
        """Test to retrieve all similar trivias without sign-in"""
        app.dependency_overrides = {}
        response = client.get(ENDPOINT_URL.format("some-id"))

        assert response.status_code == 401
        assert response.json()["message"] == "Could not validate credentials"
