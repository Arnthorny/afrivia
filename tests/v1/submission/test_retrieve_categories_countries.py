import pytest

from unittest.mock import MagicMock
from pytest_mock import MockerFixture

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.schemas.submission import ACE, CategoryEnum
from main import app

ENDPOINT_URL_CATEGORIES = "/api/v1/submissions/categories"
ENDPOINT_URL_COUNTRIES = "/api/v1/submissions/countries"

mocked_db = MagicMock(spec=Session)


def db_session_mock():
    yield mocked_db


@pytest.fixture
def client():
    client = TestClient(app)
    yield client


class TestRetrieveSubmissionCategoriesAndCountries:

    def test_get_countries_success(self, client, mocker: MockerFixture):
        """Test to verify response for getting list of countries."""
        response = client.get(ENDPOINT_URL_COUNTRIES)

        assert response.status_code == 200
        assert response.json().get("data", []) == [country.value for country in ACE]

    def test_get_categories_success(self, client, mocker: MockerFixture):
        """Test to verify response for getting list of categories."""
        response = client.get(ENDPOINT_URL_CATEGORIES)

        assert response.status_code == 200
        assert response.json().get("data", []) == [
            category.value for category in CategoryEnum
        ]
