import pytest

from app.services.clinic_assistant_service import ClinicAssistantService


def test_greeting_returns_welcome_message():
    service = ClinicAssistantService()

    response = service.get_response("hello")

    assert response == "Hello! Welcome to ClinicAI. How can I help you?"


def test_appointment_question_returns_guidance():
    service = ClinicAssistantService()

    response = service.get_response("appointment")

    assert "reception" in response.lower()


def test_unknown_question_returns_safe_fallback():
    service = ClinicAssistantService()

    response = service.get_response("What is the weather?")

    assert "could not find a verified answer" in response.lower()


def test_empty_message_raises_value_error():
    service = ClinicAssistantService()

    with pytest.raises(ValueError, match="Message is required"):
        service.get_response("")


def test_non_string_message_raises_value_error():
    service = ClinicAssistantService()

    with pytest.raises(ValueError, match="Message is required"):
        service.get_response(None)
