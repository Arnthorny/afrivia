from unittest.mock import MagicMock
from pytest_mock import MockerFixture
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.routes.submission import mod_service
from api.v1.schemas.submission import RetrieveSubmissionForModSchema
from api.v1.services.submission import submission_service
from main import app


db_session_mock = MagicMock(spec=Session)


def db_session_mock_fn():
    yield db_session_mock


client = TestClient(app)


ENDPOINT = "/api/v1/assigned-submissions/{}"


class TestRetrieveSingleSubmissionForMods:

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

    # Retrieve single assigned submission for a moderator
    def test_retrieve_single_submission(self, mocker: MockerFixture):

        subm = mocker.Mock(question="Who are you?", moderator_id="mod_id")
        mocker.patch.object(
            RetrieveSubmissionForModSchema, "model_validate", return_value=[]
        )

        db_session_mock.query().filter_by().first.return_value = subm

        response = client.get(ENDPOINT.format("submission-id"))
        assert response.status_code == 200
        assert response.json()["data"] == []

    # Retrieve single nonexistent submission for a moderator
    def test_retrieve_single_submission_nonexistent(self, mocker: MockerFixture):

        db_session_mock.query().filter_by().first.return_value = None

        response = client.get(ENDPOINT.format("non-existent-submission-id"))
        assert response.status_code == 404
        assert response.json()["message"] == "Submission not found"

    # Retrieve single unassigned submission for a moderator
    def test_retrieve_single_unassigned_submission(self, mocker: MockerFixture):

        subm = mocker.Mock(question="Who are you?", moderator_id="unassigned_mod_id")
        mocker.patch.object(
            RetrieveSubmissionForModSchema, "model_validate", return_value=[]
        )

        db_session_mock.query().filter_by().first.return_value = subm

        response = client.get(ENDPOINT.format("submission-id"))
        assert response.status_code == 403
        assert (
            response.json()["message"]
            == "You do not have permission to access this resource"
        )

    # Retrieve single submission for a unauthenticated user
    def test_retrieve_single_submission_unauthenticated(self, mocker: MockerFixture):

        subm = mocker.Mock(question="Who are you?", moderator_id="unassigned_mod_id")
        mocker.patch.object(
            RetrieveSubmissionForModSchema, "model_validate", return_value=[]
        )

        app.dependency_overrides = {}

        response = client.get(ENDPOINT.format("submission-id"))
        assert response.status_code == 401
        assert response.json()["message"] == "Could not validate credentials"
