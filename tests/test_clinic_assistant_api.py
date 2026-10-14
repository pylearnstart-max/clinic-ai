
import logging
from unittest.mock import patch

from run import app
from tests.test_app import auth_headers


def test_assistant_chat_returns_response():
    client = app.test_client()

    with patch(
        "app.api.clinic_assistant_api.assistant_service.get_response",
        return_value="Hello! Welcome to ClinicAI. How can I help you."
    ):
        response = client.post(
            "/api/assistant/chat",
            json={"message": "hello"},
            headers=auth_headers()
        )

    assert response.status_code == 200
    assert "Welcome to ClinicAI" in response.get_json()["response"]


def test_assistant_chat_requires_message():
    client = app.test_client()

    response = client.post(
        "/api/assistant/chat",
        json={},
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Message is required"


def test_assistant_chat_rejects_empty_message():
    client = app.test_client()

    response = client.post(
        "/api/assistant/chat",
        json={"message": "   "},
        headers=auth_headers()
    )

    assert response.status_code == 400


def test_assistant_chat_rejects_non_object_json():
    client = app.test_client()

    response = client.post(
        "/api/assistant/chat",
        json=["hello"],
        headers=auth_headers()
    )

    assert response.status_code == 400


def test_assistant_chat_requires_authentication():
    client = app.test_client()

    response = client.post(
        "/api/assistant/chat",
        json={"message": "hello"}
    )

    assert response.status_code == 401


def test_assistant_chat_rejects_missing_json_body():
    client = app.test_client()

    response = client.post(
        "/api/assistant/chat",
        data="hello",
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Request body must be a JSON object"
    )


def test_assistant_chat_handles_unknown_question():
    client = app.test_client()

    with patch(
        "app.api.clinic_assistant_api.assistant_service.get_response",
        return_value=(
            "I could not find a verified answer. "
            "Please contact the clinic for assistance."
        )
    ):
        response = client.post(
            "/api/assistant/chat",
            json={"message": "What is the weather on Mars?"},
            headers=auth_headers()
        )

    assert response.status_code == 200
    assert response.get_json()["response"] == (
        "I could not find a verified answer. "
        "Please contact the clinic for assistance."
    )


def test_assistant_chat_rejects_non_string_message():
    client = app.test_client()

    response = client.post(
        "/api/assistant/chat",
        json={"message": 12345},
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Message is required"


def test_assistant_chat_logs_unexpected_error(caplog):
    client = app.test_client()

    with patch(
        "app.api.clinic_assistant_api.assistant_service.get_response",
        side_effect=RuntimeError("simulated internal failure")
    ):
        with caplog.at_level(logging.ERROR):
            response = client.post(
                "/api/assistant/chat",
                json={"message": "hello"},
                headers=auth_headers()
            )

    assert response.status_code == 500
    assert response.get_json() == {
        "error": "Internal server error"
    }
    assert "Unexpected error in Clinic Assistant API" in caplog.text
    assert "simulated internal failure" in caplog.text

def test_rag_api_returns_answer():
    client = app.test_client()

    with patch(
        "app.api.clinic_assistant_api.rag_service.answer_question",
        return_value=(
            "Based on the demo clinic FAQ:\n\n"
            "Clinic Timings: Monday to Saturday, 9 AM to 6 PM."
        )
    ):
        response = client.post(
            "/api/ai/ask",
            json={"question": "What are the clinic timings?"},
            headers=auth_headers()
        )

    assert response.status_code == 200
    data = response.get_json()
    assert data["question"] == "What are the clinic timings?"
    assert "Clinic Timings" in data["answer"]


def test_rag_api_requires_authentication():
    client = app.test_client()

    response = client.post(
        "/api/ai/ask",
        json={"question": "What are the clinic timings?"}
    )

    assert response.status_code == 401


def test_rag_api_requires_question():
    client = app.test_client()

    response = client.post(
        "/api/ai/ask",
        json={},
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Question is required"


def test_rag_api_rejects_non_string_question():
    client = app.test_client()

    response = client.post(
        "/api/ai/ask",
        json={"question": 123},
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Question is required"


def test_rag_api_rejects_non_object_json():
    client = app.test_client()

    response = client.post(
        "/api/ai/ask",
        json=["hello"],
        headers=auth_headers()
    )

    assert response.status_code == 400


def test_rag_api_handles_unexpected_error(caplog):
    client = app.test_client()

    with patch(
        "app.api.clinic_assistant_api.rag_service.answer_question",
        side_effect=RuntimeError("simulated RAG failure")
    ):
        with caplog.at_level(logging.ERROR):
            response = client.post(
                "/api/ai/ask",
                json={"question": "What are the clinic timings?"},
                headers=auth_headers()
            )

    assert response.status_code == 500
    assert response.get_json() == {
        "error": "Internal server error"
    }
    assert "Unexpected error in ClinicAI RAG API" in caplog.text
    assert "simulated RAG failure" in caplog.text
