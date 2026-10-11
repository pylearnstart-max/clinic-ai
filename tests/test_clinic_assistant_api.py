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
