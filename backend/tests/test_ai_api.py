from unittest.mock import patch
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from Api.ai import router
from Api.dependencies import get_current_user


app = FastAPI()
app.include_router(router)
client = TestClient(app)


def customer_user():
    return {
        "user_uuid": str(uuid4()),
        "role": "customer",
    }


def technician_user():
    return {
        "user_uuid": str(uuid4()),
        "role": "technician",
    }


def setup_user(user):
    app.dependency_overrides[get_current_user] = lambda: user


def teardown_user():
    app.dependency_overrides.clear()


@patch("Api.ai.answer_ai_question")
def test_ask_ai_success(mock_answer):
    user = customer_user()
    setup_user(user)

    mock_answer.return_value = {
        "question": "How do I book a service?",
        "sql": "",
        "result_count": 0,
        "results": [],
        "answer": "Open your Customer Dashboard.",
    }

    try:
        response = client.post(
            "/ai/ask",
            json={"question": "How do I book a service?"},
        )

        assert response.status_code == 200
        assert response.json()["answer"] == "Open your Customer Dashboard."

        mock_answer.assert_called_once_with(
            question="How do I book a service?",
            user_uuid=user["user_uuid"],
            role="customer",
        )
    finally:
        teardown_user()


@patch("Api.ai.answer_ai_question")
def test_ask_ai_value_error_returns_400(mock_answer):
    setup_user(customer_user())
    mock_answer.side_effect = ValueError("Unsupported question")

    try:
        response = client.post(
            "/ai/ask",
            json={"question": "What is the weather?"},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Unsupported question"
    finally:
        teardown_user()


@patch("Api.ai.answer_ai_question")
def test_ask_ai_permission_error_returns_403(mock_answer):
    setup_user(technician_user())
    mock_answer.side_effect = PermissionError("Account could not be verified")

    try:
        response = client.post(
            "/ai/ask",
            json={"question": "Show my jobs"},
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Account could not be verified"
    finally:
        teardown_user()


@patch("Api.ai.answer_ai_question")
def test_ask_ai_unexpected_error_returns_500(mock_answer):
    setup_user(customer_user())
    mock_answer.side_effect = RuntimeError("Unexpected failure")

    try:
        response = client.post(
            "/ai/ask",
            json={"question": "How do I book a service?"},
        )

        assert response.status_code == 500
        assert response.json()["detail"] == "Unable to process the AI question."
    finally:
        teardown_user()


def test_ask_ai_rejects_empty_question():
    setup_user(customer_user())

    try:
        response = client.post(
            "/ai/ask",
            json={"question": ""},
        )

        assert response.status_code == 422
    finally:
        teardown_user()


def test_ask_ai_rejects_question_over_1000_characters():
    setup_user(customer_user())

    try:
        response = client.post(
            "/ai/ask",
            json={"question": "x" * 1001},
        )

        assert response.status_code == 422
    finally:
        teardown_user()
