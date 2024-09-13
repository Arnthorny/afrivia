from sqlalchemy.orm import Session
import unittest
from pytest_mock import MockerFixture
import pytest

mock_db_store = [
    {
        "question": "In what year was the African Union established?",
        "incorrect_options": ["2005", "1993", "1999"],
        "correct_option": "2001",
        "difficulty": "easy",
        "submission_note": None,
        "category": "General Knowledge",
        "countries": [],
        "id": "066dfa7d-f307-7974-8000-a3ee98a563f3",
        "status": "pending",
        "created_at": "2024-09-10T02:58:55.149655+01:00",
    },
    {
        "question": "Who is the current president of Algeria?",
        "incorrect_options": ["Lil Wayne", "George Bush", "Barack Obama"],
        "correct_option": "Abdelmadjid Tebboune",
        "difficulty": "easy",
        "submission_note": None,
        "category": "General Knowledge",
        "countries": ["Algeria"],
        "id": "066dfa4f-de25-7b53-8000-6730fbe651bf",
        "status": "pending",
        "created_at": "2024-09-10T02:46:37.863201+01:00",
    },
    {
        "question": "Whose face is present on the five hundred naira note?",
        "incorrect_options": ["Tinubu", "Kamala", "Harrison"],
        "correct_option": "Nnamdi Azikiwe",
        "difficulty": "easy",
        "submission_note": None,
        "category": "General Knowledge",
        "countries": ["Nigeria"],
        "id": "066dfa48-83c8-7c0d-8000-1857173fd0d5",
        "status": "rejected",
        "created_at": "2024-09-10T02:44:40.194681+01:00",
    },
    {
        "question": "Whose face is present on the ten naira note?",
        "incorrect_options": ["Trump", "Icheke", "Obi"],
        "correct_option": "Alvan Ikoku",
        "difficulty": "easy",
        "submission_note": None,
        "category": "General Knowledge",
        "countries": ["Nigeria"],
        "id": "066dfa22-e281-7d82-8000-b80215b771f0",
        "status": "rejected",
        "created_at": "2024-09-10T02:34:38.125340+01:00",
    },
    {
        "question": "Who is the present governor of Lagos?",
        "incorrect_options": ["Pavlov", "Durov", "Emenike"],
        "correct_option": "Sanwo Olu",
        "difficulty": "easy",
        "submission_note": None,
        "category": "General Knowledge",
        "countries": ["Nigeria"],
        "id": "066dfa0d-9d61-7748-8000-b4e4ec4bd938",
        "status": "approved",
        "created_at": "2024-09-10T02:28:57.806201+01:00",
    },
    {
        "question": "Who is the former governor of Lagos?",
        "incorrect_options": ["Pavlov", "Durov", "Emenike"],
        "correct_option": "Ambode",
        "difficulty": "easy",
        "submission_note": None,
        "category": "General Knowledge",
        "countries": ["Nigeria"],
        "id": "066dfa0a-d2e9-743d-8000-5d9a086d1d5e",
        "status": "approved",
        "created_at": "2024-09-10T02:28:13.134585+01:00",
    },
]


def mock_fetch_paginated(db: Session, skip: int, limit: int, filters: dict[str]):
    print(db, skip, limit, filters)
    mock_data = {
        "items": [],
        "total": 0,
        "total_pages": 0,
        "page": 1,
    }
    mock_data["total"] = sum(
        1
        for item in filter(
            lambda x: x.status == filters["status"] if filters["status"] else x,
            mock_db_store,
        )
    )
    i = 1

    mock_data["total_pages"] = int(mock_data["total"] / limit) + int(
        mock_data["total"] % limit > 0
    )

    for sub in mock_db_store:
        if i > limit:
            break
        if sub["status"] == filters["status"] or filters["status"] is None:
            mock_data["items"].append(sub)
            i += 1

    return mock_data


@pytest.skip("Not complete", allow_module_level=True)
class TestSubmissionServiceFunctions:

    @classmethod
    def setup_class(cls):
        # app.dependency_overrides[get_db] = db_session_mock_fn
        # app.dependency_overrides[mod_service.get_current_mod] = lambda: MagicMock(
        #     id="mod_id"
        # )
        pass

    @classmethod
    def teardown_class(cls):
        # app.dependency_overrides = {}
        pass

    # Retrieve all submissions for a moderator with default pagination
    def test_fetch_default_pagination(self, mocker: MockerFixture):
        # assert response.json()["message"] == "Submissions retrieved successfully"
        # assert len(response.json()["data"]["items"]) == min(5, len(mock_db_store))
        # assert response.json()["data"]["items"][0] in mock_db_store

        pass
