from unittest.mock import MagicMock
from pytest_mock import MockerFixture
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.routes.submission import mod_service
from api.v1.services.submission import submission_service
from main import app



db_session_mock = MagicMock(spec=Session)


def db_session_mock_fn():
    yield db_session_mock


client = TestClient(app)


ENDPOINT = "/api/v1/assigned-submissions"


class TestRetrieveSubmissionForMods:

    @classmethod
    def setup_class(cls):
        app.dependency_overrides[get_db] = db_session_mock_fn
        app.dependency_overrides[mod_service.get_current_mod] = lambda: MagicMock(
            id="mod_id"
        )
        pass

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    # Retrieve all submissions for a moderator with default pagination
    def test_retrieve_all_submissions_default_pagination(self, mocker: MockerFixture):

        mock_obj = mocker.patch.object(
            submission_service, "fetch_paginated", return_value=[]
        )

        response = client.get(ENDPOINT)
        assert response.status_code == 200

        mock_obj.assert_called_once_with(
            db=db_session_mock,
            skip=0,
            limit=5,
            filters={"moderator_id": "mod_id", "status": None},
        )

    # Retrieve submissions with a specific status for a moderator
    def test_retrieve_submissions_specific_status(self, mocker):
        mock_obj = mocker.patch.object(
            submission_service, "fetch_paginated", return_value=[]
        )

        response = client.get(f"{ENDPOINT}?status=approved")
        assert response.status_code == 200

        mock_obj.assert_called_once_with(
            db=db_session_mock,
            skip=0,
            limit=5,
            filters={"moderator_id": "mod_id", "status": "approved"},
        )

        assert response.json()["message"] == "Submissions retrieved successfully"
        assert response.json()["data"] == []

    # Retrieve submissions with custom page and limit values
    def test_retrieve_submissions_custom_page_limit(self, mocker):

        mock_obj = mocker.patch.object(
            submission_service, "fetch_paginated", return_value=[]
        )

        response = client.get(f"{ENDPOINT}?status=approved&page=2")
        assert response.status_code == 200

        mock_obj.assert_called_once_with(
            db=db_session_mock,
            skip=5,
            limit=5,
            filters={"moderator_id": "mod_id", "status": "approved"},
        )

        assert response.json()["message"] == "Submissions retrieved successfully"
        assert response.json()["data"] == []

    # Correctly calculated skip value based on page and limit
    def test_correct_skip_value_calculation(self, mocker):

        mock_obj = mocker.patch.object(
            submission_service, "fetch_paginated", return_value=[]
        )

        response = client.get(f"{ENDPOINT}?status=pending&page=3&limit=10")
        assert response.status_code == 200

        mock_obj.assert_called_once_with(
            db=db_session_mock,
            skip=20,
            limit=10,
            filters={"moderator_id": "mod_id", "status": "pending"},
        )

        assert response.json()["message"] == "Submissions retrieved successfully"
        assert response.json()["data"] == []

    # Retrieve submissions with an invalid status value
    def test_retrieve_submissions_invalid_status(self):
        response = client.get(f"{ENDPOINT}?status=what&page=3&limit=10")
        assert response.status_code == 422
        assert "errors" in response.json()

    # Retrieve submissions with page number less than 1
    def test_retrieve_submissions_page_number_less_than_1(self):
        response = client.get(f"{ENDPOINT}?status=pending&page=0&limit=10")
        assert response.status_code == 422
        assert "errors" in response.json()

    # Retrieve submissions with limit value less than 1
    def test_retrieve_submissions_limit_less_than_1(self):
        response = client.get(f"{ENDPOINT}?status=pending&page=1&limit=0")
        assert response.status_code == 422
        assert "errors" in response.json()

    # Ensure the moderator is authenticated before retrieving submissions
    def test_moderator_authentication_required(self):
        app.dependency_overrides = {}

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 401
        assert response.json()["message"] == "Could not validate credentials"
