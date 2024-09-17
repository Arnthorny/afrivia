import pytest

from datetime import datetime, timezone
from unittest.mock import MagicMock
from pytest_mock import MockerFixture


import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.v1.services.moderator import (
    bearer_scheme,
    mod_service,
    HTTPAuthorizationCredentials,
)
from api.db.database import get_db
from api.v1.services.submission import (
    submission_service,
    CountryService,
    CategoryService,
)
from api.v1.models.submission import Submission, SubmissionOption
from api.v1.models.category import Category
from api.v1.models.country import Country
from main import app

ENDPOINT_URL = "/api/v1/submissions"


def mock_sub(question="Who"):
    subm = Submission(
        id=str(uuid7()),
        status="pending",
        question=question,
        moderator_id="random-mod-id",
        difficulty="medium",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    subm.categories = [Category(name="Politics")]
    subm.countries = [Country(name="Algeria")]

    subm.options = [
        SubmissionOption(content="Test", is_correct=False),
        SubmissionOption(content="options", is_correct=False),
        SubmissionOption(content="for", is_correct=False),
        SubmissionOption(content="mocked data", is_correct=True),
    ]

    return subm


mocked_db = MagicMock(spec=Session)


def db_session_mock():
    yield mocked_db


@pytest.fixture
def client():
    client = TestClient(app)
    yield client


class TestRetrieveAllSubmissions:

    @classmethod
    def setup_class(cls):
        app.dependency_overrides[get_db] = db_session_mock
        app.dependency_overrides[mod_service.get_current_admin] = lambda: MagicMock(
            id="mod_id"
        )

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_get_all_submissions(self, client, mocker: MockerFixture):
        """Test to verify response for getting all submissions."""

        mock_submission_data = [
            mock_sub(),
            mock_sub("Who is the first?"),
        ]

        mocker.patch.object(
            submission_service, "fetch_all", return_value=mock_submission_data
        )
        response = client.get(ENDPOINT_URL.format(""))

        assert response.status_code == 200
        assert (
            response.json()["data"][0]["question"] == mock_submission_data[0].question
        )
        assert (
            response.json()["data"][1]["difficulty"]
            == mock_submission_data[1].difficulty
        )

    def test_get_all_submissions_empty(self, client, mocker: MockerFixture):
        """Test to verify response for getting all submissions, even when there are
        none."""

        mock_submission_data = []
        mocker.patch.object(
            submission_service, "fetch_all", return_value=mock_submission_data
        )
        response = client.get(ENDPOINT_URL.format(""))

        assert response.status_code == 200
        assert response.json().get("data") == []

    def test_retrieve_all_submissions_unauthenticated(self, client, mocker):
        """Test to retrieve all submissions without sign-in"""
        app.dependency_overrides = {}
        response = client.get(ENDPOINT_URL.format(""))

        assert response.status_code == 401
        assert response.json()["message"] == "Could not validate credentials"

    def test_delete_submission_forbidden(self, client, mocker):
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
        response = client.get(ENDPOINT_URL.format("some-id"))
        assert response.status_code == 403
        assert (
            response.json()["message"]
            == "You do not have permission to access this resource"
        )
