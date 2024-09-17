import pytest

from datetime import datetime, timezone
from unittest.mock import MagicMock
from pytest_mock import MockerFixture

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from api.v1.services.moderator import (
    bearer_scheme,
    mod_service,
    HTTPAuthorizationCredentials,
)

from api.db.database import get_db
from api.v1.services.submission import submission_service
from api.v1.models.submission import Submission
from main import app

ENDPOINT_URL = "/api/v1/submissions/{}"


def mock_sub(question="Who"):
    subm = Submission(
        id="some-id",
        status="pending",
        question=question,
        moderator_id="random-mod-id",
        difficulty="medium",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    return subm


mocked_db = MagicMock(spec=Session)


def db_session_mock():
    yield mocked_db


@pytest.fixture
def client():
    client = TestClient(app)
    yield client


class TestClassDeleteSubmission:
    @classmethod
    def setup_class(cls):
        app.dependency_overrides[get_db] = db_session_mock
        app.dependency_overrides[mod_service.get_current_admin] = lambda: MagicMock(
            id="mod_id"
        )

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    # Successfully delete submission from the database
    def test_delete_submission_success(self, client: TestClient, mocker: MockerFixture):
        mock_s = mock_sub()
        mock_fetch = mocker.patch.object(
            submission_service, "delete", return_value=mock_s
        )

        response = client.delete(ENDPOINT_URL.format("some-id"))

        assert response.status_code == 204
        mock_fetch.assert_called_once_with(db=mocked_db, id=mock_s.id)

    # Invalid id
    def test_delete_submission_invalid_id(self, client, mocker):

        mocker.patch.object(mocked_db, "get", return_value=None)

        response = client.delete(ENDPOINT_URL.format("some-id"))
        assert response.status_code == 404
        assert response.json()["message"] == "Submission not found"

    # Handling unauthenticated request
    def test_delete_submission_unauthenticated(self, client):
        app.dependency_overrides = {}

        response = client.delete(ENDPOINT_URL.format("some-id"))
        assert response.status_code == 401
        assert response.json()["message"] == "Could not validate credentials"

    # Handling forbidden request
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
        response = client.delete(ENDPOINT_URL.format("some-id"))
        assert response.status_code == 403
        assert (
            response.json()["message"]
            == "You do not have permission to access this resource"
        )
