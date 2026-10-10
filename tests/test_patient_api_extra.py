
import pytest

from run import app
from app.api.patient_api import patient_service
from app.models.patient import Patient


@pytest.fixture
def client(monkeypatch):
    from app.auth import auth_decorator

    app.config["TESTING"] = True

    monkeypatch.setattr(
        auth_decorator.auth_service,
        "verify_token",
        lambda token: {"user_id": "1", "role": "admin"}
    )

    with app.test_client() as test_client:
        test_client.environ_base["HTTP_AUTHORIZATION"] = "Bearer test-token"
        yield test_client


@pytest.fixture
def mock_patient_service(monkeypatch):
    from app.api import patient_api as module

    return module.patient_service


def sample_patient():
    return Patient(
        patient_id=1,
        name="Ravi",
        age=30,
        gender="Male",
        phone="9876543210",
        address="Hyderabad"
    )


# -------- POST /api/patients --------

def test_add_patient_invalid_json(client, monkeypatch):
    monkeypatch.setattr(
        patient_service,
        "add_patient",
        lambda **kwargs: pytest.fail("Service should not be called")
    )

    response = client.post(
        "/api/patients",
        data="not json",
        content_type="application/json"
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "A JSON object is required"
    }


def test_add_patient_value_error(client, monkeypatch):
    def raise_error(**kwargs):
        raise ValueError("Patient name is required")

    monkeypatch.setattr(patient_service, "add_patient", raise_error)

    response = client.post("/api/patients", json={})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Patient name is required"


def test_add_patient_internal_error(client, monkeypatch):
    def raise_error(**kwargs):
        raise RuntimeError("Database unavailable")

    monkeypatch.setattr(patient_service, "add_patient", raise_error)

    response = client.post(
        "/api/patients",
        json={"name": "Ravi", "phone": "9876543210"}
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal server error"


# -------- GET /api/patients --------

def test_get_all_patients_success(client, monkeypatch):
    monkeypatch.setattr(
        patient_service,
        "get_all_patients",
        lambda: [sample_patient()]
    )

    response = client.get("/api/patients")

    assert response.status_code == 200
    assert response.get_json() == [{
        "patient_id": 1,
        "name": "Ravi",
        "age": 30,
        "gender": "Male",
        "phone": "9876543210",
        "address": "Hyderabad"
    }]


def test_get_all_patients_internal_error(client, monkeypatch):
    def raise_error():
        raise RuntimeError("Database unavailable")

    monkeypatch.setattr(
        patient_service,
        "get_all_patients",
        raise_error
    )

    response = client.get("/api/patients")

    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal server error"


# -------- GET /api/patients/<id> --------

def test_get_patient_by_id_not_found(client, monkeypatch):
    monkeypatch.setattr(
        patient_service,
        "get_patient_by_id",
        lambda patient_id: None
    )

    response = client.get("/api/patients/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Patient not found"


def test_get_patient_by_id_value_error(client, monkeypatch):
    def raise_error(patient_id):
        raise ValueError("Patient ID must be greater than 0")

    monkeypatch.setattr(
        patient_service,
        "get_patient_by_id",
        raise_error
    )

    response = client.get("/api/patients/0")

    # Flask's <int:patient_id> route accepts 0,
    # then the service raises ValueError.
    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Patient ID must be greater than 0"
    )


def test_get_patient_by_id_internal_error(client, monkeypatch):
    def raise_error(patient_id):
        raise RuntimeError("Database unavailable")

    monkeypatch.setattr(
        patient_service,
        "get_patient_by_id",
        raise_error
    )

    response = client.get("/api/patients/1")

    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal server error"


# -------- PUT /api/patients/<id> --------

def test_update_patient_invalid_json(client, monkeypatch):
    monkeypatch.setattr(
        patient_service,
        "update_patient",
        lambda **kwargs: pytest.fail("Service should not be called")
    )

    response = client.put(
        "/api/patients/1",
        data="not json",
        content_type="application/json"
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "A JSON object is required"


def test_update_patient_not_found(client, monkeypatch):
    monkeypatch.setattr(
        patient_service,
        "update_patient",
        lambda **kwargs: False
    )

    response = client.put(
        "/api/patients/999",
        json={
            "name": "Ravi",
            "age": 30,
            "gender": "Male",
            "phone": "9876543210",
            "address": "Hyderabad"
        }
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Patient not found"


def test_update_patient_value_error(client, monkeypatch):
    def raise_error(**kwargs):
        raise ValueError("Patient name is required")

    monkeypatch.setattr(
        patient_service,
        "update_patient",
        raise_error
    )

    response = client.put("/api/patients/1", json={})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Patient name is required"


def test_update_patient_internal_error(client, monkeypatch):
    def raise_error(**kwargs):
        raise RuntimeError("Database unavailable")

    monkeypatch.setattr(
        patient_service,
        "update_patient",
        raise_error
    )

    response = client.put(
        "/api/patients/1",
        json={"name": "Ravi"}
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal server error"


# -------- DELETE /api/patients/<id> --------

def test_delete_patient_not_found(client, monkeypatch):
    monkeypatch.setattr(
        patient_service,
        "delete_patient",
        lambda patient_id: False
    )

    response = client.delete("/api/patients/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Patient not found"


def test_delete_patient_value_error(client, monkeypatch):
    def raise_error(patient_id):
        raise ValueError("Patient ID must be greater than 0")

    monkeypatch.setattr(
        patient_service,
        "delete_patient",
        raise_error
    )

    response = client.delete("/api/patients/0")

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Patient ID must be greater than 0"
    )


def test_delete_patient_internal_error(client, monkeypatch):
    def raise_error(patient_id):
        raise RuntimeError("Database unavailable")

    monkeypatch.setattr(
        patient_service,
        "delete_patient",
        raise_error
    )

    response = client.delete("/api/patients/1")

    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal server error"

