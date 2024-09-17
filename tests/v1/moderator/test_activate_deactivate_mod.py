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

ENDPOINT_URL_ACTIVATE = "/api/v1/moderators/{}/activate"
ENDPOINT_URL_DEACTIVATE = "/api/v1/moderators/{}/deactivate"


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


class TestActivateDeactivateModerator:

    @classmethod
    def setup_class(cls):
        app.dependency_overrides[get_db] = db_session_mock

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_activate_moderator_success(self, client, mocker: MockerFixture):
        """Test to verify successful activation of moderator."""
        mocked_adm = mock_mod(is_admin=True)
        mocked_mod = mock_mod()
        app.dependency_overrides[mod_service.get_current_admin] = lambda: mocked_adm

        m_patch = mocker.patch.object(mod_service, "fetch", return_value=mocked_mod)

        response = client.patch(ENDPOINT_URL_ACTIVATE.format(mocked_mod.id))

        m_patch.assert_called_once_with(db=mocked_db, id=mocked_mod.id)

        assert response.status_code == 200
        assert response.json()["data"]["is_active"] == True
        assert mocked_mod.is_active == True

    def test_deactivate_moderator_success_admin(self, client, mocker: MockerFixture):
        """Test to verify successful deactivation of moderator by admin"""
        mocked_adm = mock_mod(is_admin=True)
        mocked_mod = mock_mod()
        app.dependency_overrides[mod_service.get_current_mod] = lambda: mocked_adm

        m_patch = mocker.patch.object(mod_service, "fetch", return_value=mocked_mod)
        response = client.patch(ENDPOINT_URL_DEACTIVATE.format(mocked_mod.id))

        m_patch.assert_called_once_with(db=mocked_db, id=mocked_mod.id)

        assert response.status_code == 200
        assert response.json()["data"]["is_active"] == False
        assert mocked_mod.is_active == False

    def test_deactivate_moderator_success_same_mod(self, client, mocker: MockerFixture):
        """Test to verify successful deactivation of moderator."""
        # app.dependency_overrides[mod_service.get_current_admin] = lambda: MagicMock(
        # is_admin=False
        # )
        """Test to verify successful deactivation of moderator."""
        mocked_mod = mock_mod(is_active=True)
        app.dependency_overrides[mod_service.get_current_mod] = lambda: mocked_mod

        m_patch = mocker.patch.object(mod_service, "fetch", return_value=mocked_mod)

        response = client.patch(ENDPOINT_URL_DEACTIVATE.format(mocked_mod.id))

        m_patch.assert_called_once_with(db=mocked_db, id=mocked_mod.id)

        assert response.status_code == 200
        assert response.json()["data"]["is_active"] == False
        assert mocked_mod.is_active == False

    def test_activate_moderator_unsuccessful_not_admin(
        self, client, mocker: MockerFixture
    ):
        """Test to verify unsuccessful activation of moderator."""
        # app.dependency_overrides[mod_service.get_current_admin] = lambda: MagicMock(
        # is_admin=False
        # )
        mocked_mod = mock_mod(is_admin=False)
        app.dependency_overrides[mod_service.get_current_admin] = lambda: mocked_mod

        response = client.patch(ENDPOINT_URL_ACTIVATE.format(str(uuid7())))
        assert response.status_code == 403

    def test_deactivate_moderator_unsuccessful_not_admin(
        self, client, mocker: MockerFixture
    ):
        """Test to verify unsuccessful deactivation of moderator."""
        # app.dependency_overrides[mod_service.get_current_admin] = lambda: MagicMock(
        # is_admin=False
        # )
        mocker.patch.object(
            mod_service, "get_current_mod", return_value=MagicMock(is_admin=False)
        )
        response = client.patch(ENDPOINT_URL_DEACTIVATE.format(str(uuid7())))

        assert response.status_code == 403

    def test_deactivate_moderator_unsuccessful_not_same_mod(
        self, client, mocker: MockerFixture
    ):
        """Test to verify unsuccessful deactivation of moderator."""
        # app.dependency_overrides[mod_service.get_current_admin] = lambda: MagicMock(
        # is_admin=False
        # )
        """Test to verify successful deactivation of moderator."""
        mocked_mod = mock_mod()
        app.dependency_overrides[mod_service.get_current_mod] = lambda: mocked_mod

        m_patch = mocker.patch.object(mod_service, "fetch", return_value=mocked_mod)

        response = client.patch(ENDPOINT_URL_DEACTIVATE.format("not-same-id"))

        assert response.status_code == 403

    def test_deactivate_moderator_invalid_id(self, client, mocker: MockerFixture):
        """Test to verify successful deactivation of moderator."""
        app.dependency_overrides[mod_service.get_current_mod] = lambda: MagicMock(
            id="mod_id", is_admin=True
        )
        mocked_mod = None
        mocker.patch.object(mod_service, "fetch", return_value=mocked_mod)

        response = client.patch(ENDPOINT_URL_DEACTIVATE.format("random-id"))
        assert response.status_code == 404
        assert response.json()["message"] == "Moderator not found"
