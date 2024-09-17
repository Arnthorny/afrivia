import pytest

from unittest.mock import MagicMock
from pytest_mock import MockerFixture

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.services.submission import submission_service
from main import app

ENDPOINT_URL = "/api/v1/submissions/stats"

mocked_db = MagicMock(spec=Session)


def db_session_mock():
    yield mocked_db


@pytest.fixture
def client():
    client = TestClient(app)
    yield client


class TestRetrieveSubmissionStats:

    @classmethod
    def setup_class(cls):
        app.dependency_overrides[get_db] = db_session_mock

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_get_stats_success(self, client, mocker: MockerFixture):
        """Test to verify response for getting submission stats."""

        mock_s = {"total": 5, "approved": 2, "rejected": 2, "pending": 1, "awaiting": 0}
        mock_fetch = mocker.patch.object(
            submission_service, "fetch_submission_stats", return_value=mock_s
        )

        response = client.get(ENDPOINT_URL)

        assert response.status_code == 200
        mock_fetch.assert_called_once_with(db=mocked_db)
        assert response.json().get("data", {}).get("total") == mock_s["total"]
