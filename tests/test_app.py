
import os
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch
from datetime import date, time

import jwt
from dotenv import load_dotenv

from run import app
from app.models.doctor import Doctor
from app.models.patient import Patient


load_dotenv()


# ---------------- JWT TEST TOKEN ----------------

def create_test_token():
    secret_key = os.getenv("JWT_SECRET_KEY")

    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    now = datetime.now(timezone.utc)

    payload = {
        "sub": "1",
        "role": "admin",
        "iat": now,
        "exp": now + timedelta(minutes=30),
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm="HS256"
    )


def auth_headers():
    token = create_test_token()

    return {
        "Authorization": f"Bearer {token}"
    }


# ---------------- HOME API TEST ----------------

def test_home_endpoint():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "ClinicAI API is running"
    }


# ---------------- PATIENT API BASIC TESTS ----------------

def test_get_patients_endpoint():
    client = app.test_client()

    response = client.get(
        "/api/patients",
        headers=auth_headers()
    )

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_create_patient_requires_json_object():
    client = app.test_client()

    response = client.post(
        "/api/patients",
        json=[],
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "A JSON object is required"


def test_get_nonexistent_patient_returns_404():
    client = app.test_client()

    response = client.get(
        "/api/patients/999999",
        headers=auth_headers()
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Patient not found"


def test_update_patient_requires_json_object():
    client = app.test_client()

    response = client.put(
        "/api/patients/999999",
        json=[],
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "A JSON object is required"


def test_delete_nonexistent_patient_returns_404():
    client = app.test_client()

    response = client.delete(
        "/api/patients/999999",
        headers=auth_headers()
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Patient not found"


# ---------------- PATIENT SUCCESS TESTS ----------------

def test_create_patient_success():
    client = app.test_client()

    with patch(
        "app.api.patient_api.patient_service.add_patient",
        return_value=True
    ):
        response = client.post(
            "/api/patients",
            json={
                "name": "Test Patient",
                "age": 30,
                "gender": "Female",
                "phone": "9876543210",
                "address": "Hyderabad"
            },
            headers=auth_headers()
        )

    assert response.status_code == 201
    assert response.get_json()["message"] == "Patient added successfully"


def test_get_existing_patient_success():
    client = app.test_client()

    patient = Patient(
        name="Test Patient",
        age=30,
        gender="Female",
        phone="9876543210",
        address="Hyderabad",
        patient_id=101
    )

    with patch(
        "app.api.patient_api.patient_service.get_patient_by_id",
        return_value=patient
    ):
        response = client.get(
            "/api/patients/101",
            headers=auth_headers()
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["patient_id"] == 101
    assert data["name"] == "Test Patient"
    assert data["age"] == 30


def test_update_existing_patient_success():
    client = app.test_client()

    with patch(
        "app.api.patient_api.patient_service.update_patient",
        return_value=True
    ):
        response = client.put(
            "/api/patients/101",
            json={
                "name": "Updated Patient",
                "age": 31,
                "gender": "Female",
                "phone": "9876543210",
                "address": "Hyderabad"
            },
            headers=auth_headers()
        )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Patient updated successfully"


def test_delete_existing_patient_success():
    client = app.test_client()

    with patch(
        "app.api.patient_api.patient_service.delete_patient",
        return_value=True
    ):
        response = client.delete(
            "/api/patients/101",
            headers=auth_headers()
        )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Patient deleted successfully"


# ---------------- DOCTOR API BASIC TESTS ----------------

def test_get_doctors_endpoint():
    client = app.test_client()

    response = client.get("/doctors")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_create_doctor_requires_json_object():
    client = app.test_client()

    response = client.post("/doctors", json=[])

    assert response.status_code == 400
    assert response.get_json()["error"] == "A JSON object is required"


def test_get_nonexistent_doctor_returns_404():
    client = app.test_client()

    response = client.get("/doctors/999999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Doctor not found"


def test_update_doctor_requires_json_object():
    client = app.test_client()

    response = client.put("/doctors/999999", json=[])

    assert response.status_code == 400
    assert response.get_json()["error"] == "A JSON object is required"


def test_delete_nonexistent_doctor_returns_404():
    client = app.test_client()

    response = client.delete("/doctors/999999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Doctor not found"


# ---------------- DOCTOR SUCCESS TESTS ----------------

def test_create_doctor_success():
    client = app.test_client()

    with patch(
        "app.api.doctor_api.doctor_service.add_doctor",
        return_value=True
    ):
        response = client.post("/doctors", json={
            "name": "Dr. Test Kumar",
            "specialization": "Cardiology",
            "phone": "9876543210",
            "email": "test@example.com",
            "consultation_fee": 500
        })

    assert response.status_code == 201
    assert response.get_json()["message"] == "Doctor added successfully"


def test_get_existing_doctor_success():
    client = app.test_client()

    doctor = Doctor(
        doctor_id=101,
        name="Dr. Test Kumar",
        specialization="Cardiology",
        phone="9876543210",
        email="test@example.com",
        consultation_fee=500,
        is_available=True
    )

    with patch(
        "app.api.doctor_api.doctor_service.get_doctor_by_id",
        return_value=doctor
    ):
        response = client.get("/doctors/101")

    assert response.status_code == 200

    data = response.get_json()

    assert data["doctor_id"] == 101
    assert data["name"] == "Dr. Test Kumar"
    assert data["consultation_fee"] == 500.0


def test_update_existing_doctor_success():
    client = app.test_client()

    with patch(
        "app.api.doctor_api.doctor_service.update_doctor",
        return_value=True
    ):
        response = client.put("/doctors/101", json={
            "name": "Dr. Test Kumar",
            "specialization": "Cardiology",
            "phone": "9876543210",
            "email": "test@example.com",
            "consultation_fee": 700,
            "is_available": True
        })

    assert response.status_code == 200
    assert response.get_json()["message"] == "Doctor updated successfully"


def test_delete_existing_doctor_success():
    client = app.test_client()

    with patch(
        "app.api.doctor_api.doctor_service.delete_doctor",
        return_value=True
    ):
        response = client.delete("/doctors/101")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Doctor deleted successfully"


# ---------------- APPOINTMENT API TEST ----------------

def test_get_appointments_endpoint():
    client = app.test_client()

    response = client.get("/appointments")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


# ---------------- APPOINTMENT SUCCESS TESTS ----------------

def create_test_appointment():
    return SimpleNamespace(
        appointment_id=101,
        patient_id=1,
        doctor_id=2,
        appointment_date=date(2026, 10, 10),
        appointment_time=time(10, 30),
        reason="General checkup",
        status="Scheduled"
    )


def test_create_appointment_success():
    client = app.test_client()
    appointment = create_test_appointment()

    with patch(
        "app.api.appointment_api.appointment_service.add_appointment",
        return_value=appointment
    ):
        response = client.post("/appointments", json={
            "patient_id": 1,
            "doctor_id": 2,
            "appointment_date": "2026-10-10",
            "appointment_time": "10:30",
            "reason": "General checkup"
        })

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Appointment booked successfully"
    assert data["appointment"]["appointment_id"] == 101


def test_get_existing_appointment_success():
    client = app.test_client()
    appointment = create_test_appointment()

    with patch(
        "app.api.appointment_api.appointment_service.get_all_appointments",
        return_value=[appointment]
    ):
        response = client.get("/appointments/101")

    assert response.status_code == 200

    data = response.get_json()

    assert data["appointment_id"] == 101
    assert data["patient_id"] == 1
    assert data["doctor_id"] == 2
    assert data["reason"] == "General checkup"


def test_update_appointment_success():
    client = app.test_client()
    appointment = create_test_appointment()

    with patch(
        "app.api.appointment_api.appointment_service.update_appointment",
        return_value=appointment
    ):
        response = client.put("/appointments/101", json={
            "reason": "Follow-up checkup"
        })

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Appointment updated successfully"
    assert data["appointment"]["appointment_id"] == 101


def test_delete_appointment_success():
    client = app.test_client()

    with patch(
        "app.api.appointment_api.appointment_service.delete_appointment"
    ):
        response = client.delete("/appointments/101")

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Appointment deleted successfully"
    assert data["appointment_id"] == 101


# ---------------- APPOINTMENT ERROR TESTS ----------------

def test_update_nonexistent_appointment_returns_404():
    client = app.test_client()

    with patch(
        "app.api.appointment_api.appointment_service.update_appointment",
        side_effect=ValueError("Appointment not found")
    ):
        response = client.put("/appointments/999999", json={
            "reason": "Follow-up checkup"
        })

    assert response.status_code == 404
    assert response.get_json()["error"] == "Appointment not found"


def test_delete_nonexistent_appointment_returns_404():
    client = app.test_client()

    with patch(
        "app.api.appointment_api.appointment_service.delete_appointment",
        side_effect=ValueError("Appointment not found")
    ):
        response = client.delete("/appointments/999999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Appointment not found"


# ---------------- CENTRAL ERROR HANDLER TEST ----------------

def test_central_500_error_handler():
    original_testing = app.testing
    original_propagate = app.config.get("PROPAGATE_EXCEPTIONS")
    original_home = app.view_functions["home"]

    def broken_home():
        raise RuntimeError("Test-only simulated error")

    try:
        app.testing = False
        app.config["PROPAGATE_EXCEPTIONS"] = False
        app.view_functions["home"] = broken_home

        response = app.test_client().get("/")

        assert response.status_code == 500
        assert response.get_json() == {
            "error": "Internal server error"
        }

    finally:
        app.view_functions["home"] = original_home
        app.testing = original_testing

        if original_propagate is None:
            app.config.pop("PROPAGATE_EXCEPTIONS", None)
        else:
           app.config["PROPAGATE_EXCEPTIONS"] = original_propagate

# ---------------- PATIENT AUTHENTICATION TESTS ----------------

def test_get_patients_without_token_returns_401():
    client = app.test_client()

    response = client.get("/api/patients")

    assert response.status_code == 401


def test_get_patient_by_id_without_token_returns_401():
    client = app.test_client()

    response = client.get("/api/patients/101")

    assert response.status_code == 401


def test_create_patient_without_token_returns_401():
    client = app.test_client()

    response = client.post(
        "/api/patients",
        json={
            "name": "Test Patient",
            "age": 30,
            "gender": "Female",
            "phone": "9876543210",
            "address": "Hyderabad"
        }
    )

    assert response.status_code == 401


def test_update_patient_without_token_returns_401():
    client = app.test_client()

    response = client.put(
        "/api/patients/101",
        json={"name": "Updated Patient"}
    )

    assert response.status_code == 401


def test_delete_patient_without_token_returns_401():
    client = app.test_client()

    response = client.delete("/api/patients/101")

    assert response.status_code == 401
