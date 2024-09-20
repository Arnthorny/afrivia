import pytest

from datetime import datetime, timezone
from unittest.mock import MagicMock
from pytest_mock import MockerFixture


import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid_extensions import uuid7

from api.v1.services.moderator import (
    bearer_scheme,
    mod_service,
    HTTPAuthorizationCredentials,
)
from api.db.database import get_db
from api.v1.services.trivia import trivia_service, CountryService, CategoryService
from api.v1.models.trivia import Trivia, TriviaOption
from api.v1.models.category import Category
from api.v1.models.country import Country
from main import app

ENDPOINT_URL = "/api/v1/questions"


def mock_trivia(question="Who"):
    triv = Trivia(
        id=str(uuid7()),
        question=question,
        difficulty="medium",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    triv.categories = [Category(name="Politics")]
    triv.countries = [Country(name="Algeria")]

    triv.options = [
        TriviaOption(content="Test", is_correct=False),
        TriviaOption(content="options", is_correct=False),
        TriviaOption(content="for", is_correct=False),
        TriviaOption(content="mocked data", is_correct=True),
    ]

    return triv


mocked_db = MagicMock(spec=Session)


def db_session_mock():
    yield mocked_db


@pytest.fixture
def client():
    client = TestClient(app)
    yield client


class TestRetrieveTrivias:

    @classmethod
    def setup_class(cls):
        app.dependency_overrides[get_db] = db_session_mock

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_get_questions_with_no_params(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting questions without passing a parameter."""

        params = {}
        limit = params.get("amount", 1)
        mock_trivia_data = [mock_trivia()] * limit

        filter_obj = {}

        mock_db_query_fn = mocker.patch(
            "api.v1.services.trivia.query_for_question_retrieval"
        )

        mocked_db.scalars().all.return_value = mock_trivia_data

        response = client.get(ENDPOINT_URL, params=params)

        assert response.status_code == 200
        mock_db_query_fn.assert_called_once_with(filters=filter_obj, limit=limit)
        assert response.json()["data"][0]["question"] == mock_trivia_data[0].question

        mocked_db.reset_mock()

    def test_get_questions_with_difficulty_param(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting questions whilst passing just the difficulty param."""

        params = {"difficulty": "easy"}
        limit = params.get("amount", 1)
        mock_trivia_data = [mock_trivia()] * limit

        filter_obj = {"difficulty": mocker.ANY}

        mock_db_query_fn = mocker.patch(
            "api.v1.services.trivia.query_for_question_retrieval"
        )
        mocked_db.scalars().all.return_value = mock_trivia_data

        response = client.get(ENDPOINT_URL, params=params)

        assert response.status_code == 200
        mock_db_query_fn.assert_called_once_with(filters=filter_obj, limit=limit)

        # Assert equality of binary expressions
        _, kwargs = mock_db_query_fn.call_args
        assert str(kwargs["filters"]["difficulty"].compile()) == str(
            (Trivia.difficulty == params["difficulty"]).compile()
        )

        assert response.json()["data"][0]["question"] == mock_trivia_data[0].question
        mocked_db.reset_mock()

    def test_get_questions_with_category_param(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting questions whilst passing just the category param."""

        params = {"category": "Science"}
        limit = params.get("amount", 1)

        mock_trivia_data = [mock_trivia()] * limit
        filter_obj = {"category": mocker.ANY}
        mock_db_query_fn = mocker.patch(
            "api.v1.services.trivia.query_for_question_retrieval"
        )
        mocked_db.scalars().all.return_value = mock_trivia_data

        response = client.get(ENDPOINT_URL, params=params)

        assert response.status_code == 200
        mock_db_query_fn.assert_called_once_with(filters=filter_obj, limit=limit)

        # Assert equality of binary expressions
        _, kwargs = mock_db_query_fn.call_args
        assert str(kwargs["filters"]["category"].compile()) == str(
            (Category.name == params["category"]).compile()
        )

        assert response.json()["data"][0]["question"] == mock_trivia_data[0].question
        mocked_db.reset_mock()

    def test_get_questions_with_country_param(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting questions whilst passing just the country param."""

        params = {"country": "Ghana"}
        limit = params.get("amount", 1)

        mock_trivia_data = [mock_trivia()] * limit
        filter_obj = params
        mock_db_query_fn = mocker.patch(
            "api.v1.services.trivia.query_for_question_retrieval"
        )
        mocked_db.scalars().all.return_value = mock_trivia_data

        response = client.get(ENDPOINT_URL, params=params)

        assert response.status_code == 200
        mock_db_query_fn.assert_called_once_with(filters=filter_obj, limit=limit)

        assert response.json()["data"][0]["question"] == mock_trivia_data[0].question
        mocked_db.reset_mock()

    def test_get_questions_with_amount_param(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting questions whilst passing just the amount param."""

        params = {"amount": 5}
        limit = params.get("amount", 1)

        mock_trivia_data = [mock_trivia()] * limit
        filter_obj = {}
        mock_db_query_fn = mocker.patch(
            "api.v1.services.trivia.query_for_question_retrieval"
        )
        mocked_db.scalars().all.return_value = mock_trivia_data

        response = client.get(ENDPOINT_URL, params=params)

        assert response.status_code == 200
        mock_db_query_fn.assert_called_once_with(filters=filter_obj, limit=limit)

        assert response.json()["data"][0]["question"] == mock_trivia_data[0].question
        assert (
            response.json()["data"][3]["difficulty"] == mock_trivia_data[3].difficulty
        )

        assert len(response.json()["data"]) == len(mock_trivia_data)
        mocked_db.reset_mock()

    def test_get_questions_with_two_params_first(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting questions whilst passing just two params."""

        params = {"country": "Chad", "difficulty": "easy"}
        limit = params.get("amount", 1)

        mock_trivia_data = [mock_trivia()] * limit
        filter_obj = {"country": mocker.ANY, "difficulty": mocker.ANY}
        mock_db_query_fn = mocker.patch(
            "api.v1.services.trivia.query_for_question_retrieval"
        )
        mocked_db.scalars().all.return_value = mock_trivia_data

        response = client.get(ENDPOINT_URL, params=params)

        assert response.status_code == 200
        mock_db_query_fn.assert_called_once_with(filters=filter_obj, limit=limit)

        # Assert equality of binary expressions
        _, kwargs = mock_db_query_fn.call_args
        assert str(kwargs["filters"]["difficulty"].compile()) == str(
            (Trivia.difficulty == params["difficulty"]).compile()
        )

        assert response.json()["data"][0]["question"] == mock_trivia_data[0].question

        mocked_db.reset_mock()

    def test_get_questions_with_two_params_second(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting questions whilst passing just two params."""

        params = {"category": "Science", "difficulty": "hard"}
        limit = params.get("amount", 1)

        mock_trivia_data = [mock_trivia()] * limit
        filter_obj = {"category": mocker.ANY, "difficulty": mocker.ANY}
        mock_db_query_fn = mocker.patch(
            "api.v1.services.trivia.query_for_question_retrieval"
        )
        mocked_db.scalars().all.return_value = mock_trivia_data

        response = client.get(ENDPOINT_URL, params=params)

        assert response.status_code == 200
        mock_db_query_fn.assert_called_once_with(filters=filter_obj, limit=limit)

        # Assert equality of binary expressions
        _, kwargs = mock_db_query_fn.call_args
        assert str(kwargs["filters"]["difficulty"].compile()) == str(
            (Trivia.difficulty == params["difficulty"]).compile()
        )
        assert str(kwargs["filters"]["category"].compile()) == str(
            (Category.name == params["category"]).compile()
        )

        assert response.json()["data"][0]["question"] == mock_trivia_data[0].question
        mocked_db.reset_mock()

    def test_get_questions_with_two_params_third(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting questions whilst passing just two params."""

        params = {"category": "Science", "amount": 4}
        limit = params.get("amount", 1)

        mock_trivia_data = [mock_trivia()] * limit
        filter_obj = {"category": mocker.ANY}
        mock_db_query_fn = mocker.patch(
            "api.v1.services.trivia.query_for_question_retrieval"
        )
        mocked_db.scalars().all.return_value = mock_trivia_data

        response = client.get(ENDPOINT_URL, params=params)

        assert response.status_code == 200
        mock_db_query_fn.assert_called_once_with(filters=filter_obj, limit=limit)

        # Assert equality of binary expressions
        _, kwargs = mock_db_query_fn.call_args
        assert str(kwargs["filters"]["category"].compile()) == str(
            (Category.name == params["category"]).compile()
        )

        assert len(response.json()["data"]) == len(mock_trivia_data)
        assert response.json()["data"][0]["question"] == mock_trivia_data[0].question
        mocked_db.reset_mock()

    def test_get_questions_with_two_params_fourth(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting questions whilst passing just two params."""

        params = {"country": "Niger", "difficulty": "hard"}
        limit = params.get("amount", 1)

        mock_trivia_data = [mock_trivia()] * limit
        filter_obj = {"difficulty": mocker.ANY, "country": params["country"]}
        mock_db_query_fn = mocker.patch(
            "api.v1.services.trivia.query_for_question_retrieval"
        )
        mocked_db.scalars().all.return_value = mock_trivia_data

        response = client.get(ENDPOINT_URL, params=params)

        assert response.status_code == 200
        mock_db_query_fn.assert_called_once_with(filters=filter_obj, limit=limit)

        # Assert equality of binary expressions
        _, kwargs = mock_db_query_fn.call_args
        assert str(kwargs["filters"]["difficulty"].compile()) == str(
            (Trivia.difficulty == params["difficulty"]).compile()
        )

        assert response.json()["data"][0]["question"] == mock_trivia_data[0].question
        mocked_db.reset_mock()

    def test_get_questions_with_three_params(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting questions whilst passing three params."""

        params = {"country": "Niger", "difficulty": "hard", "category": "Science"}
        limit = params.get("amount", 1)

        mock_trivia_data = [mock_trivia()] * limit
        filter_obj = {
            "difficulty": mocker.ANY,
            "country": params["country"],
            "category": mocker.ANY,
        }
        mock_db_query_fn = mocker.patch(
            "api.v1.services.trivia.query_for_question_retrieval"
        )
        mocked_db.scalars().all.return_value = mock_trivia_data

        response = client.get(ENDPOINT_URL, params=params)

        assert response.status_code == 200
        mock_db_query_fn.assert_called_once_with(filters=filter_obj, limit=limit)

        # Assert equality of binary expressions
        _, kwargs = mock_db_query_fn.call_args
        assert str(kwargs["filters"]["difficulty"].compile()) == str(
            (Trivia.difficulty == params["difficulty"]).compile()
        )
        assert str(kwargs["filters"]["category"].compile()) == str(
            (Category.name == params["category"]).compile()
        )
        assert response.json()["data"][0]["question"] == mock_trivia_data[0].question
        mocked_db.reset_mock()

    def test_get_questions_with_four_params(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting questions whilst passing three params."""

        params = {
            "country": "Niger",
            "difficulty": "hard",
            "category": "Science",
            "amount": 5,
        }
        limit = params.get("amount", 1)

        mock_trivia_data = [mock_trivia()] * limit
        filter_obj = {
            "difficulty": mocker.ANY,
            "country": params["country"],
            "category": mocker.ANY,
        }
        mock_db_query_fn = mocker.patch(
            "api.v1.services.trivia.query_for_question_retrieval"
        )
        mocked_db.scalars().all.return_value = mock_trivia_data

        response = client.get(ENDPOINT_URL, params=params)

        assert response.status_code == 200
        mock_db_query_fn.assert_called_once_with(filters=filter_obj, limit=limit)

        # Assert equality of binary expressions
        _, kwargs = mock_db_query_fn.call_args
        assert str(kwargs["filters"]["difficulty"].compile()) == str(
            (Trivia.difficulty == params["difficulty"]).compile()
        )
        assert str(kwargs["filters"]["category"].compile()) == str(
            (Category.name == params["category"]).compile()
        )
        assert response.json()["data"][0]["question"] == mock_trivia_data[0].question
        assert len(response.json()["data"]) == len(mock_trivia_data)

        mocked_db.reset_mock()

    def test_get_questions_invalid_category_param(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting questions with invalid category."""

        params = {"category": "Sci"}
        response = client.get(ENDPOINT_URL, params=params)
        assert response.status_code == 422

    def test_get_questions_invalid_difficulty_param(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting questions with invalid difficulty."""

        params = {"difficulty": "Hardest"}
        response = client.get(ENDPOINT_URL, params=params)
        assert response.status_code == 422

    def test_get_questions_invalid_country_param(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting questions with invalid country."""

        params = {"country": "Bolivia"}
        response = client.get(ENDPOINT_URL, params=params)
        assert response.status_code == 422

    def test_get_questions_invalid_amount_param(
        self, client: TestClient, mocker: MockerFixture
    ):
        """Test to verify response for getting questions with invalid amount."""

        params = {"amount": 0}
        response = client.get(ENDPOINT_URL, params=params)
        assert response.status_code == 422
