from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from Api.skills import router


app = FastAPI()
app.include_router(router)

client = TestClient(app)


@patch("Api.skills.get_all_skills")
def test_get_skills_success(mock_get_all_skills):
    mock_get_all_skills.return_value = [
        {
            "skill_id": 1,
            "skill_name": "AC Repair",
            "category": "Electrical",
            "difficulty_level": "Intermediate",
            "estimated_duration": 60,
            "description": "AC maintenance",
        }
    ]

    response = client.get("/skills")

    assert response.status_code == 200
    assert response.json()[0]["skill_name"] == "AC Repair"
    mock_get_all_skills.assert_called_once_with()


@patch("Api.skills.get_all_skills")
def test_get_skills_empty_list(mock_get_all_skills):
    mock_get_all_skills.return_value = []

    response = client.get("/skills")

    assert response.status_code == 200
    assert response.json() == []


@patch("Api.skills.get_all_skills")
def test_get_skills_handles_service_error(mock_get_all_skills):
    mock_get_all_skills.side_effect = RuntimeError("Database unavailable")

    response = client.get("/skills")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Unable to fetch skills."
    }
