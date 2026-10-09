
import pytest

from run import app
from app.api.doctor_api import doctor_service
from app.models.doctor import Doctor


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def sample_doctor():
    return Doctor(
        doctor_id=1,
        name="Dr Ravi",
        specialization="Cardiology",
        phone="9876543210",
        email="ravi@example.com",
        consultation_fee=500,
        is_available=True
    )


# POST /doctors

def test_add_doctor_invalid_json(client, monkeypatch):
    monkeypatch.setattr(
        doctor_service,
        "add_doctor",
        lambda **kwargs: pytest.fail("Service should not be called")
    )

    response = client.post(
        "/doctors",
        data="invalid",
        content_type="application/json"
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "A JSON object is required"


def test_add_doctor_success_false(client, monkeypatch):
    monkeypatch.setattr(
        doctor_service, "add_doctor", lambda **kwargs: False
    )

    response = client.post(
        "/doctors",
        json={"name": "Dr Ravi", "specialization": "Cardiology"}
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "Doctor could not be added"


def test_add_doctor_value_error(client, monkeypatch):
    def raise_error(**kwargs):
        raise ValueError("Specialization is required")

    monkeypatch.setattr(doctor_service, "add_doctor", raise_error)

    response = client.post("/doctors", json={"name": "Dr Ravi"})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Specialization is required"


def test_add_doctor_internal_error(client, monkeypatch):
    def raise_error(**kwargs):
        raise RuntimeError("Database error")

    monkeypatch.setattr(doctor_service, "add_doctor", raise_error)

    response = client.post(
        "/doctors",
        json={"name": "Dr Ravi", "specialization": "Cardiology"}
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal server error"


# GET /doctors

def test_get_all_doctors_success(client, monkeypatch):
    monkeypatch.setattr(
        doctor_service, "get_all_doctors", lambda: [sample_doctor()]
    )

    response = client.get("/doctors")

    assert response.status_code == 200
    result = response.get_json()

    assert len(result) == 1
    assert result[0]["doctor_id"] == 1
    assert result[0]["name"] == "Dr Ravi"
    assert result[0]["specialization"] == "Cardiology"
    assert result[0]["consultation_fee"] == 500.0
    assert result[0]["is_available"] is True


def test_get_all_doctors_internal_error(client, monkeypatch):
    def raise_error():
        raise RuntimeError("Database error")

    monkeypatch.setattr(
        doctor_service, "get_all_doctors", raise_error
    )

    response = client.get("/doctors")

    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal server error"


# GET /doctors/<id>

def test_get_doctor_by_id_not_found(client, monkeypatch):
    monkeypatch.setattr(
        doctor_service, "get_doctor_by_id", lambda doctor_id: None
    )

    response = client.get("/doctors/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Doctor not found"


def test_get_doctor_by_id_value_error(client, monkeypatch):
    def raise_error(doctor_id):
        raise ValueError("Doctor ID must be positive")

    monkeypatch.setattr(
        doctor_service, "get_doctor_by_id", raise_error
    )

    response = client.get("/doctors/0")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Doctor ID must be positive"


def test_get_doctor_by_id_internal_error(client, monkeypatch):
    def raise_error(doctor_id):
        raise RuntimeError("Database error")

    monkeypatch.setattr(
        doctor_service, "get_doctor_by_id", raise_error
    )

    response = client.get("/doctors/1")

    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal server error"


def test_get_doctor_by_id_success(client, monkeypatch):
    monkeypatch.setattr(
        doctor_service, "get_doctor_by_id", lambda doctor_id: sample_doctor()
    )

    response = client.get("/doctors/1")

    assert response.status_code == 200
    assert response.get_json()["email"] == "ravi@example.com"


# PUT /doctors/<id>

def test_update_doctor_invalid_json(client, monkeypatch):
    monkeypatch.setattr(
        doctor_service,
        "update_doctor",
        lambda **kwargs: pytest.fail("Service should not be called")
    )

    response = client.put(
        "/doctors/1",
        data="invalid",
        content_type="application/json"
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "A JSON object is required"


@pytest.mark.parametrize("available", ["yes", 1, None, [], {}])
def test_update_doctor_invalid_is_available(client, monkeypatch, available):
    monkeypatch.setattr(
        doctor_service,
        "update_doctor",
        lambda **kwargs: pytest.fail("Service should not be called")
    )

    response = client.put(
        "/doctors/1",
        json={
            "name": "Dr Ravi",
            "specialization": "Cardiology",
            "is_available": available
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "is_available must be true or false"
    )


def test_update_doctor_not_found(client, monkeypatch):
    monkeypatch.setattr(
        doctor_service, "update_doctor", lambda **kwargs: False
    )

    response = client.put(
        "/doctors/999",
        json={
            "name": "Dr Ravi",
            "specialization": "Cardiology",
            "consultation_fee": 500,
            "is_available": True
        }
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Doctor not found"


def test_update_doctor_value_error(client, monkeypatch):
    def raise_error(**kwargs):
        raise ValueError("Doctor name is required")

    monkeypatch.setattr(doctor_service, "update_doctor", raise_error)

    response = client.put("/doctors/1", json={"name": ""})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Doctor name is required"


def test_update_doctor_internal_error(client, monkeypatch):
    def raise_error(**kwargs):
        raise RuntimeError("Database error")

    monkeypatch.setattr(doctor_service, "update_doctor", raise_error)

    response = client.put("/doctors/1", json={"name": "Dr Ravi"})

    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal server error"


def test_update_doctor_success(client, monkeypatch):
    monkeypatch.setattr(
        doctor_service, "update_doctor", lambda **kwargs: True
    )

    response = client.put(
        "/doctors/1",
        json={
            "name": "Dr Ravi",
            "specialization": "Cardiology",
            "consultation_fee": 600,
            "is_available": False
        }
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Doctor updated successfully"


# DELETE /doctors/<id>

def test_delete_doctor_not_found(client, monkeypatch):
    monkeypatch.setattr(
        doctor_service, "delete_doctor", lambda doctor_id: False
    )

    response = client.delete("/doctors/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Doctor not found"


def test_delete_doctor_value_error(client, monkeypatch):
    def raise_error(doctor_id):
        raise ValueError("Doctor ID must be positive")

    monkeypatch.setattr(
        doctor_service, "delete_doctor", raise_error
    )

    response = client.delete("/doctors/0")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Doctor ID must be positive"


def test_delete_doctor_internal_error(client, monkeypatch):
    def raise_error(doctor_id):
        raise RuntimeError("Database error")

    monkeypatch.setattr(
        doctor_service, "delete_doctor", raise_error
    )

    response = client.delete("/doctors/1")

    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal server error"


def test_delete_doctor_success(client, monkeypatch):
    monkeypatch.setattr(
        doctor_service, "delete_doctor", lambda doctor_id: True
    )

    response = client.delete("/doctors/1")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Doctor deleted successfully"