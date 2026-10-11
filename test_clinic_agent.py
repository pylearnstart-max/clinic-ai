
import pytest

from app.agents.clinic_agent import clinic_graph


def get_response(message):
    result = clinic_graph.invoke({
        "message": message,
        "response": "",
    })
    return result["response"]


def test_hello():
    response = get_response("hello")
    assert "Welcome to ClinicAI" in response


def test_how_are_you():
    response = get_response("how r u")
    assert "I'm doing well" in response


def test_appointment():
    response = get_response("I need an appointment")
    assert "appointment information" in response


def test_appointment_spelling():
    response = get_response("i need appoinment")
    assert "appointment information" in response


def test_thank_you():
    response = get_response("thank u")
    assert "You're welcome" in response


def test_thank_you_short_form():
    response = get_response("than u")
    assert "You're welcome" in response


def test_doctor_information():
    response = get_response("show doctor information")
    assert "doctor-related information" in response


def test_clinic_timings():
    response = get_response("what are the clinic timing")
    assert "working hours" in response


def test_unknown_message():
    response = get_response("python")
    assert "Please tell me how I can help you" in response


def test_empty_message():
    response = get_response("")
    assert response == "Please enter a message."
def test_missing_message_key():
    result = clinic_graph.invoke({
        "response": "",
        "category": "",
    })

    assert result["category"] == "empty"
    assert result["response"] == "Please enter a message."
def test_appointment_routing():
    result = clinic_graph.invoke({
        "message": "I need an appointment",
        "response": "",
        "category": "",
    })

    assert result["category"] == "appointment"


def test_doctor_routing():
    result = clinic_graph.invoke({
        "message": "show doctor information",
        "response": "",
        "category": "",
    })

    assert result["category"] == "doctor"


def test_greeting_routing():
    result = clinic_graph.invoke({
        "message": "hello",
        "response": "",
        "category": "",
    })

    assert result["category"] == "greeting"

