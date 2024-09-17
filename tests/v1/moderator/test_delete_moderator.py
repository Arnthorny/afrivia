import pytest

from datetime import datetime, timezone
from unittest.mock import MagicMock
from pytest_mock import MockerFixture
from uuid_extensions import uuid7

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from api.v1.services.moderator import (
    bearer_scheme,
    mod_service,
    HTTPAuthorizationCredentials,
)

from api.db.database import get_db
from api.v1.services.submission import mod_service
from api.v1.models.moderator import Moderator
from main import app

ENDPOINT_URL = "/api/v1/moderators/{}"


def mock_mod(is_admin=False, first_name="John", is_active=False):
    mod = Moderator(
        id=str(uuid7()),
        first_name=first_name,
        last_name="Doe",
        username="johndoe",
        email="john.doe@example.com",
        password="password123",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_active=is_active,
        is_admin=is_admin,
    )

    return mod


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
        cls.mock_adm = mock_mod(is_admin=True)
        app.dependency_overrides[get_db] = db_session_mock
        app.dependency_overrides[mod_service.get_current_admin] = lambda: cls.mock_adm

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    # Successfully delete moderator from the database
    def test_delete_moderator_success(self, client: TestClient, mocker: MockerFixture):
        mock_s = mock_mod()
        mock_fetch = mocker.patch.object(mod_service, "delete", return_value=True)

        response = client.delete(ENDPOINT_URL.format(mock_s.id))

        assert response.status_code == 204
        mock_fetch.assert_called_once_with(
            db=mocked_db,
            id_target=mock_s.id,
            current_admin=TestClassDeleteSubmission.mock_adm,
        )

    # Invalid id
    def test_delete_moderator_invalid_id(self, client, mocker):

        mocker.patch.object(mocked_db, "get", return_value=None)

        response = client.delete(ENDPOINT_URL.format("some-id"))
        assert response.status_code == 404
        assert response.json()["message"] == "Moderator not found"

    # Handling unauthenticated request
    def test_delete_moderator_unauthenticated(self, client):
        app.dependency_overrides = {}

        response = client.delete(ENDPOINT_URL.format("some-id"))
        assert response.status_code == 401
        assert response.json()["message"] == "Could not validate credentials"

    # Handling forbidden request
    def test_delete_moderator_forbidden(self, client, mocker):
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
