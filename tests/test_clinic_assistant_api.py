
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