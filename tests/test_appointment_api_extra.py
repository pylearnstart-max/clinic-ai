
import pytest
from datetime import date, time

from run import app
from app.api.appointment_api import appointment_service
from app.models.appointment import Appointment


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def sample_appointment(appointment_id=1):
    return Appointment(
        appointment_id=appointment_id,
        patient_id=10,
        doctor_id=20,
        appointment_date=date(2099, 5, 20),
        appointment_time=time(10, 30),
        reason="Regular checkup",
        status="Scheduled"
    )


# POST /appointments

def test_add_appointment_invalid_json(client, monkeypatch):
    monkeypatch.setattr(
        appointment_service,
        "add_appointment",
        lambda **kwargs: pytest.fail("Service should not be called")
    )

    response = client.post(
        "/appointments",
        data="invalid",
        content_type="application/json"
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "A JSON object is required"


def test_add_appointment_value_error(client, monkeypatch):
    def raise_error(**kwargs):
        raise ValueError("Patient ID is required")

    monkeypatch.setattr(
        appointment_service, "add_appointment", raise_error
    )

    response = client.post(
        "/appointments",
        json={
            "patient_id": 10,
            "doctor_id": 20,
            "appointment_date": "2099-05-20",
            "appointment_time": "10:30",
            "reason": "Checkup"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Patient ID is required"


def test_add_appointment_internal_error(client, monkeypatch):
    def raise_error(**kwargs):
        raise RuntimeError("Database error")

    monkeypatch.setattr(
        appointment_service, "add_appointment", raise_error
    )

    response = client.post(
        "/appointments",
        json={
            "patient_id": 10,
            "doctor_id": 20,
            "appointment_date": "2099-05-20",
            "appointment_time": "10:30",
            "reason": "Checkup"
        }
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal server error"


def test_add_appointment_success(client, monkeypatch):
    monkeypatch.setattr(
        appointment_service,
        "add_appointment",
        lambda **kwargs: sample_appointment()
    )

    response = client.post(
        "/appointments",
        json={
            "patient_id": 10,
            "doctor_id": 20,
            "appointment_date": "2099-05-20",
            "appointment_time": "10:30",
            "reason": "Checkup"
        }
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["message"] == "Appointment booked successfully"
    assert body["appointment"]["appointment_id"] == 1
    assert body["appointment"]["appointment_date"] == "2099-05-20"
    assert body["appointment"]["appointment_time"] == "10:30"


# GET /appointments

def test_get_all_appointments_success(client, monkeypatch):
    monkeypatch.setattr(
        appointment_service,
        "get_all_appointments",
        lambda: [sample_appointment()]
    )

    response = client.get("/appointments")

    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["appointment_id"] == 1
    assert body[0]["reason"] == "Regular checkup"


def test_get_all_appointments_internal_error(client, monkeypatch):
    def raise_error():
        raise RuntimeError("Database error")

    monkeypatch.setattr(
        appointment_service, "get_all_appointments", raise_error
    )

    response = client.get("/appointments")

    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal server error"


# GET /appointments/<id>

def test_get_appointment_by_id_success(client, monkeypatch):
    monkeypatch.setattr(
        appointment_service,
        "get_all_appointments",
        lambda: [sample_appointment(1), sample_appointment(2)]
    )

    response = client.get("/appointments/2")

    assert response.status_code == 200
    assert response.get_json()["appointment_id"] == 2


def test_get_appointment_by_id_not_found(client, monkeypatch):
    monkeypatch.setattr(
        appointment_service,
        "get_all_appointments",
        lambda: [sample_appointment(1)]
    )

    response = client.get("/appointments/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Appointment not found"


def test_get_appointment_by_id_internal_error(client, monkeypatch):
    def raise_error():
        raise RuntimeError("Database error")

    monkeypatch.setattr(
        appointment_service, "get_all_appointments", raise_error
    )

    response = client.get("/appointments/1")

    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal server error"


# PUT /appointments/<id>

def test_update_appointment_invalid_json(client, monkeypatch):
    monkeypatch.setattr(
        appointment_service,
        "update_appointment",
        lambda *args: pytest.fail("Service should not be called")
    )

    response = client.put(
        "/appointments/1",
        data="invalid",
        content_type="application/json"
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "A JSON object is required"


def test_update_appointment_success(client, monkeypatch):
    monkeypatch.setattr(
        appointment_service,
        "update_appointment",
        lambda appointment_id, data: sample_appointment(appointment_id)
    )

    response = client.put(
        "/appointments/1",
        json={"reason": "Follow-up"}
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Appointment updated successfully"


def test_update_appointment_not_found(client, monkeypatch):
    def raise_error(appointment_id, data):
        raise ValueError("Appointment not found")

    monkeypatch.setattr(
        appointment_service, "update_appointment", raise_error
    )

    response = client.put("/appointments/999", json={"reason": "Follow-up"})

    assert response.status_code == 404
    assert response.get_json()["error"] == "Appointment not found"


def test_update_appointment_value_error(client, monkeypatch):
    def raise_error(appointment_id, data):
        raise ValueError("Invalid appointment date")

    monkeypatch.setattr(
        appointment_service, "update_appointment", raise_error
    )

    response = client.put("/appointments/1", json={"reason": "Follow-up"})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid appointment date"


def test_update_appointment_internal_error(client, monkeypatch):
    def raise_error(appointment_id, data):
        raise RuntimeError("Database error")

    monkeypatch.setattr(
        appointment_service, "update_appointment", raise_error
    )

    response = client.put("/appointments/1", json={"reason": "Follow-up"})

    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal server error"


# DELETE /appointments/<id>

def test_delete_appointment_success(client, monkeypatch):
    monkeypatch.setattr(
        appointment_service,
        "delete_appointment",
        lambda appointment_id: True
    )

    response = client.delete("/appointments/1")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Appointment deleted successfully"
    assert response.get_json()["appointment_id"] == 1


def test_delete_appointment_not_found(client, monkeypatch):
    def raise_error(appointment_id):
        raise ValueError("Appointment not found")

    monkeypatch.setattr(
        appointment_service, "delete_appointment", raise_error
    )

    response = client.delete("/appointments/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Appointment not found"


def test_delete_appointment_value_error(client, monkeypatch):
    def raise_error(appointment_id):
        raise ValueError("Appointment ID must be positive")

    monkeypatch.setattr(
        appointment_service, "delete_appointment", raise_error
    )

    response = client.delete("/appointments/0")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Appointment ID must be positive"


def test_delete_appointment_internal_error(client, monkeypatch):
    def raise_error(appointment_id):
        raise RuntimeError("Database error")

    monkeypatch.setattr(
        appointment_service, "delete_appointment", raise_error
    )

    response = client.delete("/appointments/1")

    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal server error"