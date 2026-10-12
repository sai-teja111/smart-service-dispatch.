from  types import SimpleNamespace
from  unittest.mock import MagicMock, patch

from modules.chroma_service import (
    normalize_text,
    add_service_to_chroma,
    find_keyword_service,
    find_semantic_service,
    find_service_by_problem,
    refresh_service_collection,
)


# ============================================================
# NORMALIZE TEXT
# ============================================================

def test_normalize_text():

    result = normalize_text(
        "AC-Repair / Cooling!!!   Problem"
    )

    assert result == (
        "ac repair cooling problem"
    )


def test_normalize_text_non_string():

    result = normalize_text(12345)

    assert result == "12345"


# ============================================================
# ADD SERVICE TO CHROMA
# ============================================================

@patch("modules.chroma_service.collection")
def test_add_service_to_chroma(
    mock_collection
):

    add_service_to_chroma(
        skill_id=1,
        skill_name="AC Repair",
        category="Home Appliance",
        description="AC service and repair"
    )

    mock_collection.upsert.assert_called_once_with(
        ids=["1"],
        documents=[
            (
                "Service: AC Repair. "
                "Category: Home Appliance. "
                "Description: AC service and repair"
            )
        ],
        metadatas=[
            {
                "skill_id": 1,
                "skill_name": "AC Repair",
                "category": "Home Appliance"
            }
        ]
    )


# ============================================================
# KEYWORD SERVICE - EMPTY COLLECTION
# ============================================================

@patch("modules.chroma_service.collection")
def test_find_keyword_service_empty_collection(
    mock_collection
):

    mock_collection.get.return_value = {
        "ids": [],
        "metadatas": [],
        "documents": []
    }

    result = find_keyword_service(
        "AC is not cooling"
    )

    assert result is None


# ============================================================
# KEYWORD SERVICE - EXACT + WORD + ALIAS MATCH
# ============================================================

@patch("modules.chroma_service.collection")
def test_find_keyword_service_match(
    mock_collection
):

    mock_collection.get.return_value = {
        "ids": ["1"],
        "metadatas": [
            {
                "skill_id": 1,
                "skill_name": "AC Repair",
                "category": "Home Appliance"
            }
        ],
        "documents": [
            "Service: AC Repair. "
            "Category: Home Appliance. "
            "Description: AC repair service"
        ]
    }

    result = find_keyword_service(
        "I need AC repair service"
    )

    assert result is not None

    assert result["skill_id"] == 1

    assert result["skill_name"] == "AC Repair"

    assert result["category"] == "Home Appliance"

    assert result["document"] == (
        "Service: AC Repair. "
        "Category: Home Appliance. "
        "Description: AC repair service"
    )

    assert result["match_type"] == "Keyword Match"

    assert result["score"] > 0


# ============================================================
# KEYWORD SERVICE - ALIAS MATCH
# ============================================================

@patch("modules.chroma_service.collection")
def test_find_keyword_service_alias_match(
    mock_collection
):

    mock_collection.get.return_value = {
        "ids": ["1"],
        "metadatas": [
            {
                "skill_id": 1,
                "skill_name": "AC Repair",
                "category": "Home Appliance"
            }
        ],
        "documents": [
            "Service: AC Repair"
        ]
    }

    result = find_keyword_service(
        "My air conditioner is not cooling"
    )

    assert result is not None

    assert result["skill_id"] == 1

    assert result["skill_name"] == "AC Repair"

    assert result["match_type"] == "Keyword Match"

    assert result["score"] > 0


# ============================================================
# KEYWORD SERVICE - WORD MATCH WITHOUT EXACT MATCH
# ============================================================

@patch("modules.chroma_service.collection")
def test_find_keyword_service_word_match(
    mock_collection
):

    mock_collection.get.return_value = {
        "ids": ["1"],
        "metadatas": [
            {
                "skill_id": 1,
                "skill_name": "Plumbing",
                "category": "Home Service"
            }
        ],
        "documents": [
            "Service: Plumbing"
        ]
    }

    result = find_keyword_service(
        "I need plumbing help"
    )

    assert result is not None

    assert result["skill_id"] == 1

    assert result["skill_name"] == "Plumbing"

    assert result["score"] > 0


# ============================================================
# KEYWORD SERVICE - MULTIPLE RESULTS
# ============================================================

@patch("modules.chroma_service.collection")
def test_find_keyword_service_multiple_results(
    mock_collection
):

    mock_collection.get.return_value = {
        "ids": [
            "1",
            "2"
        ],
        "metadatas": [
            {
                "skill_id": 1,
                "skill_name": "AC Repair",
                "category": "Home Appliance"
            },
            {
                "skill_id": 2,
                "skill_name": "Plumbing",
                "category": "Home Service"
            }
        ],
        "documents": [
            "AC repair service",
            "Plumbing service"
        ]
    }

    result = find_keyword_service(
        "I need AC repair"
    )

    assert result is not None

    assert result["skill_id"] == 1

    assert result["skill_name"] == "AC Repair"


# ============================================================
# KEYWORD SERVICE - NO MATCH
# ============================================================

@patch("modules.chroma_service.collection")
def test_find_keyword_service_no_match(
    mock_collection
):

    mock_collection.get.return_value = {
        "ids": [
            "1"
        ],
        "metadatas": [
            {
                "skill_id": 1,
                "skill_name": "AC Repair",
                "category": "Home Appliance"
            }
        ],
        "documents": [
            "AC repair service"
        ]
    }

    result = find_keyword_service(
        "I need painting"
    )

    assert result is None


# ============================================================
# SEMANTIC SERVICE - NO IDS
# ============================================================

@patch("modules.chroma_service.collection")
def test_find_semantic_service_no_ids(
    mock_collection
):

    mock_collection.query.return_value = {
        "ids": []
    }

    result = find_semantic_service(
        "My AC is not working"
    )

    assert result is None


# ============================================================
# SEMANTIC SERVICE - EMPTY INNER IDS
# ============================================================

@patch("modules.chroma_service.collection")
def test_find_semantic_service_empty_inner_ids(
    mock_collection
):

    mock_collection.query.return_value = {
        "ids": [[]]
    }

    result = find_semantic_service(
        "My AC is not working"
    )

    assert result is None


# ============================================================
# SEMANTIC SERVICE - SUCCESS
# ============================================================

@patch("modules.chroma_service.collection")
def test_find_semantic_service_success(
    mock_collection
):

    mock_collection.query.return_value = {
        "ids": [
            ["4"]
        ],
        "documents": [
            [
                "Service: AC Repair"
            ]
        ],
        "metadatas": [
            [
                {
                    "skill_name": "AC Repair",
                    "category": "Home Appliance"
                }
            ]
        ],
        "distances": [
            [
                0.25
            ]
        ]
    }

    result = find_semantic_service(
        "air conditioner problem"
    )

    assert result == {
        "skill_id": 4,
        "skill_name": "AC Repair",
        "category": "Home Appliance",
        "document": "Service: AC Repair",
        "distance": 0.25,
        "match_type": "Semantic Match"
    }

    mock_collection.query.assert_called_once_with(
        query_texts=[
            "air conditioner problem"
        ],
        n_results=1
    )


# ============================================================
# FIND SERVICE BY PROBLEM - KEYWORD SUCCESS
# ============================================================

@patch("modules.chroma_service.find_semantic_service")
@patch("modules.chroma_service.find_keyword_service")
def test_find_service_by_problem_keyword(
    mock_keyword,
    mock_semantic
):

    keyword_result = {
        "skill_id": 1,
        "skill_name": "AC Repair",
        "category": "Home Appliance",
        "document": "AC repair",
        "score": 190,
        "match_type": "Keyword Match"
    }

    mock_keyword.return_value = keyword_result

    result = find_service_by_problem(
        "AC is not cooling"
    )

    assert result == keyword_result

    mock_keyword.assert_called_once_with(
        "AC is not cooling"
    )

    mock_semantic.assert_not_called()


# ============================================================
# FIND SERVICE BY PROBLEM - SEMANTIC SUCCESS
# ============================================================

@patch("modules.chroma_service.find_semantic_service")
@patch("modules.chroma_service.find_keyword_service")
def test_find_service_by_problem_semantic(
    mock_keyword,
    mock_semantic
):

    mock_keyword.return_value = None

    semantic_result = {
        "skill_id": 4,
        "skill_name": "AC Repair",
        "category": "Home Appliance",
        "document": "AC repair",
        "distance": 0.2,
        "match_type": "Semantic Match"
    }

    mock_semantic.return_value = semantic_result

    result = find_service_by_problem(
        "air conditioner problem"
    )

    assert result == semantic_result

    mock_keyword.assert_called_once_with(
        "air conditioner problem"
    )

    mock_semantic.assert_called_once_with(
        "air conditioner problem"
    )


# ============================================================
# FIND SERVICE BY PROBLEM - NO MATCH
# ============================================================

@patch("modules.chroma_service.find_semantic_service")
@patch("modules.chroma_service.find_keyword_service")
def test_find_service_by_problem_no_match(
    mock_keyword,
    mock_semantic
):

    mock_keyword.return_value = None

    mock_semantic.return_value = None

    result = find_service_by_problem(
        "unknown problem"
    )

    assert result is None

    mock_keyword.assert_called_once_with(
        "unknown problem"
    )

    mock_semantic.assert_called_once_with(
        "unknown problem"
    )


# ============================================================
# REFRESH COLLECTION - NO SKILLS
# ============================================================

@patch("modules.chroma_service.get_session_context")
def test_refresh_service_collection_no_skills(
    mock_get_session_context,
):
    session = MagicMock()

    mock_get_session_context.return_value.__enter__.return_value = session
    session.exec.return_value.all.return_value = []

    with patch("builtins.print") as mock_print:
        refresh_service_collection()

    mock_get_session_context.assert_called_once()
    session.exec.assert_called_once()
    mock_print.assert_called_once_with(
        "No skills found in PostgreSQL."
    )


# ============================================================
# REFRESH COLLECTION - SKILLS WITHOUT EXISTING IDS
# ============================================================

@patch("modules.chroma_service.add_service_to_chroma")
@patch("modules.chroma_service.collection")
@patch("modules.chroma_service.get_session_context")
def test_refresh_service_collection_new_skills(
    mock_get_session_context,
    mock_collection,
    mock_add_service,
):
    skill1 = SimpleNamespace(
        skill_id=1,
        skill_name="AC Repair",
        category="Home Appliance",
        description="AC repair service",
    )

    skill2 = SimpleNamespace(
        skill_id=2,
        skill_name="Plumbing",
        category="Home Service",
        description="Plumbing service",
    )

    session = MagicMock()

    mock_get_session_context.return_value.__enter__.return_value = session
    session.exec.return_value.all.return_value = [skill1, skill2]
    mock_collection.get.return_value = {"ids": []}

    with patch("builtins.print") as mock_print:
        refresh_service_collection()

    mock_collection.delete.assert_not_called()
    assert mock_add_service.call_count == 2

    mock_add_service.assert_any_call(
        skill_id=1,
        skill_name="AC Repair",
        category="Home Appliance",
        description="AC repair service",
    )

    mock_add_service.assert_any_call(
        skill_id=2,
        skill_name="Plumbing",
        category="Home Service",
        description="Plumbing service",
    )

    mock_print.assert_called_once_with(
        "Service Chroma collection refreshed with 2 skills."
    )


# ============================================================
# REFRESH COLLECTION - EXISTING IDS
# ============================================================

@patch("modules.chroma_service.add_service_to_chroma")
@patch("modules.chroma_service.collection")
@patch("modules.chroma_service.get_session_context")
def test_refresh_service_collection_existing_ids(
    mock_get_session_context,
    mock_collection,
    mock_add_service,
):
    skill = SimpleNamespace(
        skill_id=5,
        skill_name="TV Repair",
        category="Electronics",
        description="TV repair service",
    )

    session = MagicMock()

    mock_get_session_context.return_value.__enter__.return_value = session
    session.exec.return_value.all.return_value = [skill]

    mock_collection.get.return_value = {
        "ids": ["1", "2", "3"]
    }

    with patch("builtins.print") as mock_print:
        refresh_service_collection()

    mock_collection.delete.assert_called_once_with(
        ids=["1", "2", "3"]
    )

    mock_add_service.assert_called_once_with(
        skill_id=5,
        skill_name="TV Repair",
        category="Electronics",
        description="TV repair service",
    )

    mock_print.assert_called_once_with(
        "Service Chroma collection refreshed with 1 skills."
    )
