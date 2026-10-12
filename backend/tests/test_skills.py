from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from modules.skills import view_skills


def make_skill(
    skill_id=1,
    skill_name="AC Repair",
    category="Electrical",
    difficulty_level="Intermediate",
    estimated_duration=60,
):
    return SimpleNamespace(
        skill_id=skill_id,
        skill_name=skill_name,
        category=category,
        difficulty_level=difficulty_level,
        estimated_duration=estimated_duration,
    )


def make_session(skills):
    session = MagicMock()
    session.exec.return_value.all.return_value = skills
    return session


@patch("modules.skills.get_session_context")
def test_view_skills_displays_skills(mock_context, capsys):
    session = make_session([make_skill()])
    mock_context.return_value.__enter__.return_value = session

    with patch("modules.skills.Skill.display_skill") as display:
        view_skills()

    output = capsys.readouterr().out

    assert "COMPANY SERVICES" in output
    display.assert_called_once()


@patch("modules.skills.get_session_context")
def test_view_skills_displays_multiple_skills(mock_context, capsys):
    session = make_session([
        make_skill(skill_id=1, skill_name="AC Repair"),
        make_skill(skill_id=2, skill_name="Plumbing"),
    ])
    mock_context.return_value.__enter__.return_value = session

    with patch("modules.skills.Skill.display_skill") as display:
        view_skills()

    assert display.call_count == 2
    assert capsys.readouterr().out.count(
        "-------------------------------------------"
    ) == 2


@patch("modules.skills.get_session_context")
def test_view_skills_when_no_skills(mock_context, capsys):
    session = make_session([])
    mock_context.return_value.__enter__.return_value = session

    view_skills()

    assert "No Services Available." in capsys.readouterr().out


@patch("modules.skills.get_session_context")
def test_view_skills_handles_database_error(mock_context, capsys):
    mock_context.side_effect = RuntimeError("Database unavailable")

    view_skills()

    output = capsys.readouterr().out

    assert "Error :" in output
    assert "Database unavailable" in output


@patch("modules.skills.get_session_context")
def test_view_skills_handles_display_error(mock_context, capsys):
    session = make_session([make_skill()])
    mock_context.return_value.__enter__.return_value = session

    with patch(
        "modules.skills.Skill.display_skill",
        side_effect=RuntimeError("Display failed"),
    ):
        view_skills()

    output = capsys.readouterr().out

    assert "Error :" in output
    assert "Display failed" in output
