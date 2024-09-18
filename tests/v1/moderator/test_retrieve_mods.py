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
from api.v1.models.moderator import Moderator
from main import app

ENDPOINT_URL = "/api/v1/moderators"


def mock_mod(is_active=True, first_name="John"):
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
        is_admin=False,
    )

    return mod


mocked_db = MagicMock(spec=Session)


def db_session_mock():
    yield mocked_db


@pytest.fixture
def client():
    client = TestClient(app)
    yield client


class TestRetrieveAllModerators:

    @classmethod
    def setup_class(cls):
        app.dependency_overrides[get_db] = db_session_mock
        app.dependency_overrides[mod_service.get_current_admin] = lambda: MagicMock(
            id="mod_id"
        )

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_get_all_moderators(self, client, mocker: MockerFixture):
        """Test to verify response for getting all moderators."""

        mock_data = [
            mock_mod(),
            mock_mod(first_name="Whoo?"),
        ]

        mocker.patch.object(mod_service, "fetch_all", return_value=mock_data)
        response = client.get(ENDPOINT_URL)

        assert response.status_code == 200
        assert response.json()["data"][0]["first_name"] == mock_data[0].first_name
        assert response.json()["data"][1]["first_name"] == mock_data[1].first_name

    def test_get_moderator_by_email(self, client: TestClient, mocker: MockerFixture):
        """Test to verify response for getting moderator by email param."""

        mock_data = mock_mod(first_name="Whoo?")

        mock_fetch = mocker.patch.object(
            mod_service, "fetch_by_email", return_value=mock_data
        )
        response = client.get(ENDPOINT_URL, params={"email": mock_data.email})

        assert response.status_code == 200
        assert response.json()["data"]["first_name"] == mock_data.first_name
        mock_fetch.assert_called_once_with(
            db=mocked_db, email=mock_data.email, raise_404=True
        )

    def test_get_moderator_by_id(self, client: TestClient, mocker: MockerFixture):
        """Test to verify response for getting moderator by id param."""

        mock_data = mock_mod()

        mock_fetch = mocker.patch.object(mod_service, "fetch", return_value=mock_data)
        response = client.get(ENDPOINT_URL, params={"id": mock_data.id})

        assert response.status_code == 200
        assert response.json()["data"]["first_name"] == mock_data.first_name
        mock_fetch.assert_called_once_with(
            db=mocked_db, id=mock_data.id, raise_404=True
        )

    def test_get_moderator_by_invalid_email_string(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting moderator by malformed email param."""

        # mock_data = mock_mod(first_name="Whoo?")

        # mock_fetch = mocker.patch.object(
        #     mod_service, "fetch_by_email", return_value=mock_data
        # )
        response = client.get(ENDPOINT_URL, params={"email": "malformed-email"})
        assert response.status_code == 422

    def test_get_moderator_by_id_not_found(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to unsuccessful request for getting moderator by id param."""

        mock_fetch = mocker.patch.object(mocked_db, "get", return_value=None)
        response = client.get(ENDPOINT_URL, params={"id": "random-id"})

        assert response.status_code == 404
        assert response.json()["message"] == "Moderator not found"
        mock_fetch.assert_called_once_with(Moderator, "random-id")

    def test_get_moderator_by_email_not_found(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to unsuccessful request for getting moderator by email param."""

        # mock_fetch = mocker.patch.object(mocked_db, "get", return_value=None)
        mocked_db.query().filter().first.return_value = None
        response = client.get(ENDPOINT_URL, params={"email": "valid@email.com"})
        mocked_db.reset_mock()

        assert response.status_code == 404
        assert response.json()["message"] == "Moderator not found"

    def test_get_all_moderators_empty(self, client, mocker: MockerFixture):
        """Test to verify response for getting all moderators, even when there are
        none."""

        mock_data = []
        mocker.patch.object(mod_service, "fetch_all", return_value=mock_data)
        response = client.get(ENDPOINT_URL)

        assert response.status_code == 200
        assert response.json().get("data") == []

    def test_retrieve_all_moderators_unauthenticated(self, client, mocker):
        """Test to retrieve all moderators without sign-in"""
        app.dependency_overrides = {}
        response = client.get(ENDPOINT_URL)

        assert response.status_code == 401
        assert response.json()["message"] == "Could not validate credentials"

    def test_retrieve_all_moderators_forbidden(self, client, mocker):
        """Test to retrieve all moderators when not admin"""
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
        response = client.get(ENDPOINT_URL)
        assert response.status_code == 403
        assert (
            response.json()["message"]
            == "You do not have permission to access this resource"
        )
