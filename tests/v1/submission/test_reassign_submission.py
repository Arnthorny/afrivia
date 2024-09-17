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
from api.v1.services.submission import submission_service
from api.v1.models.submission import Submission, SubmissionOption
from api.v1.models.category import Category
from api.v1.models.country import Country
from api.v1.models.moderator import Moderator
from main import app

ENDPOINT_URL = "/api/v1/submissions/{}/reassign"


def mock_sub(question="Who"):
    subm = Submission(
        id=str(uuid7()),
        status="pending",
        question=question,
        moderator_id=str(uuid7()),
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


def mock_mod(is_active=True):
    mod = Moderator(
        id=str(uuid7()),
        first_name="John",
        last_name="Doe",
        username="johndoe",
        email="john.doe@example.com",
        password="password123",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_active=is_active,
    )

    return mod


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

    def test_reassign_submission_success(self, client, mocker: MockerFixture):
        """Test to verify reassignment of submission."""
        mocked_sub = mock_sub()
        mocked_mod = mock_mod()

        m_patch = mocker.patch.object(mod_service, "fetch", return_value=mocked_mod)
        s_patch = mocker.patch.object(
            submission_service, "fetch", return_value=mocked_sub
        )

        response = client.patch(
            ENDPOINT_URL.format(mocked_sub.id), json={"moderator_id": mocked_mod.id}
        )

        m_patch.assert_called_once_with(db=mocked_db, id=mocked_mod.id)
        s_patch.assert_called_once_with(db=mocked_db, id=mocked_sub.id, raise_404=True)

        assert response.status_code == 200
        assert response.json()["data"]["moderator_id"] == mocked_mod.id
        assert response.json()["data"]["question"] == mocked_sub.question

    def test_reassign_submission_invalid_mod(self, client, mocker: MockerFixture):
        """Test to verify unsuccessful reassignment of submission as mod is nonexistent"""
        mocked_sub = mock_sub()

        m_patch = mocker.patch.object(mod_service, "fetch", return_value=None)
        s_patch = mocker.patch.object(
            submission_service, "fetch", return_value=mocked_sub
        )
        r_id = str(uuid7())
        response = client.patch(
            ENDPOINT_URL.format(mocked_sub.id), json={"moderator_id": r_id}
        )

        m_patch.assert_called_once_with(db=mocked_db, id=r_id)
        s_patch.assert_called_once_with(db=mocked_db, id=mocked_sub.id, raise_404=True)

        assert response.status_code == 400
        assert response.json()["message"] == "Moderator does not exist or is inactive"

    def test_reassign_submission_mod_inactive(self, client, mocker: MockerFixture):
        """Test to verify unsuccessful reassignment of submission as mod is inactive."""
        mocked_sub = mock_sub()
        mocked_mod = mock_mod(is_active=False)

        m_patch = mocker.patch.object(mod_service, "fetch", return_value=mocked_mod)
        s_patch = mocker.patch.object(
            submission_service, "fetch", return_value=mocked_sub
        )

        response = client.patch(
            ENDPOINT_URL.format(mocked_sub.id), json={"moderator_id": mocked_mod.id}
        )

        m_patch.assert_called_once_with(db=mocked_db, id=mocked_mod.id)
        s_patch.assert_called_once_with(db=mocked_db, id=mocked_sub.id, raise_404=True)

        assert response.status_code == 400
        assert response.json()["message"] == "Moderator does not exist or is inactive"

    def test_reassign_submission_invalid_mod_id(self, client, mocker: MockerFixture):
        """Test to verify unsuccessful reassignment of submission as mod id format is incorrect."""
        response = client.patch(
            ENDPOINT_URL.format("random-id"), json={"moderator_id": "random-mod-id"}
        )

        assert response.status_code == 422

    def test_reassign_submissions_unauthenticated(self, client, mocker):
        """Test to reassign submissions without sign-in"""
        app.dependency_overrides = {}
        response = client.patch(ENDPOINT_URL.format("sub-id"))

        assert response.status_code == 401
        assert response.json()["message"] == "Could not validate credentials"

    def test_reassign_submissions_forbidden(self, client, mocker):
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
        response = client.patch(ENDPOINT_URL.format("some-id"))
        assert response.status_code == 403
        assert (
            response.json()["message"]
            == "You do not have permission to access this resource"
        )
