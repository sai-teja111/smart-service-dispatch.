from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from modules.skills_service import get_all_skills


def make_skill(
    skill_id=1,
    skill_name="AC Repair",
    category="Electrical",
    difficulty_level="Intermediate",
    estimated_duration=60,
    description="Repair and maintenance of air conditioners",
):
    return SimpleNamespace(
        skill_id=skill_id,
        skill_name=skill_name,
        category=category,
        difficulty_level=difficulty_level,
        estimated_duration=estimated_duration,
        description=description,
    )


def make_session(skills):
    session = MagicMock()
    session.exec.return_value.all.return_value = skills
    return session


@patch("modules.skills_service.get_session_context")
def test_get_all_skills_returns_skill_data(mock_context):
    session = make_session([make_skill()])
    mock_context.return_value.__enter__.return_value = session

    result = get_all_skills()

    assert result == [
        {
            "skill_id": 1,
            "skill_name": "AC Repair",
            "category": "Electrical",
            "difficulty_level": "Intermediate",
            "estimated_duration": 60,
            "description": "Repair and maintenance of air conditioners",
        }
    ]


@patch("modules.skills_service.get_session_context")
def test_get_all_skills_returns_empty_list(mock_context):
    session = make_session([])
    mock_context.return_value.__enter__.return_value = session

    assert get_all_skills() == []


@patch("modules.skills_service.get_session_context")
def test_get_all_skills_returns_multiple_skills(mock_context):
    session = make_session([
        make_skill(skill_id=2, skill_name="Plumbing"),
        make_skill(skill_id=1, skill_name="AC Repair"),
    ])
    mock_context.return_value.__enter__.return_value = session

    result = get_all_skills()

    assert len(result) == 2
    assert result[0]["skill_id"] == 2
    assert result[1]["skill_id"] == 1


@patch("modules.skills_service.get_session_context")
def test_get_all_skills_propagates_database_error(mock_context):
    mock_context.side_effect = RuntimeError("Database unavailable")

    with pytest.raises(RuntimeError, match="Database unavailable"):
        get_all_skills()


@patch("modules.skills_service.get_session_context")
def test_get_all_skills_propagates_query_error(mock_context):
    session = MagicMock()
    mock_context.return_value.__enter__.return_value = session
    session.exec.side_effect = RuntimeError("Query failed")

    with pytest.raises(RuntimeError, match="Query failed"):
        get_all_skills()
