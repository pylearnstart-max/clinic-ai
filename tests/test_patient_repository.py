
from unittest.mock import Mock

import pytest

from app.models.patient import Patient
from app.repositories.patient_repository import PatientRepository


@pytest.fixture
def setup_repository(monkeypatch):
    import app.repositories.patient_repository as module

    cursor = Mock()
    connection = Mock()

    connection.cursor.return_value = cursor

    monkeypatch.setattr(
        module,
        "get_connection",
        lambda: connection
    )

    repository = PatientRepository()

    return repository, cursor, connection


def make_patient(patient_id=1):
    return Patient(
        patient_id=patient_id,
        name="Ravi",
        age=30,
        gender="Male",
        phone="9876543210",
        address="Hyderabad"
    )


# ---------------- ADD PATIENT ----------------

def test_add_patient_success(setup_repository):
    repository, cursor, connection = setup_repository
    patient = make_patient()

    result = repository.add_patient(patient)

    assert result is True
    cursor.execute.assert_called_once()

    query = cursor.execute.call_args.args[0]
    assert "INSERT INTO patients" in query

    assert cursor.execute.call_args.args[1:] == (
        patient.name,
        patient.age,
        patient.gender,
        patient.phone,
        patient.address
    )

    connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


# ---------------- GET ALL PATIENTS ----------------

def test_get_all_patients_success(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.fetchall.return_value = [
        (1, "Ravi", 30, "Male", "9876543210", "Hyderabad"),
        (2, "Sita", 25, "Female", "9123456780", "Warangal")
    ]

    result = repository.get_all_patients()

    assert len(result) == 2
    assert all(isinstance(patient, Patient) for patient in result)

    assert result[0].patient_id == 1
    assert result[0].name == "Ravi"
    assert result[0].age == 30
    assert result[0].gender == "Male"
    assert result[0].phone == "9876543210"
    assert result[0].address == "Hyderabad"

    assert result[1].patient_id == 2
    assert result[1].name == "Sita"

    cursor.execute.assert_called_once()
    cursor.fetchall.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_get_all_patients_empty(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.fetchall.return_value = []

    result = repository.get_all_patients()

    assert result == []
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


# ---------------- GET PATIENT BY ID ----------------

def test_get_patient_by_id_success(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.fetchone.return_value = (
        1, "Ravi", 30, "Male", "9876543210", "Hyderabad"
    )

    result = repository.get_patient_by_id(1)

    assert isinstance(result, Patient)
    assert result.patient_id == 1
    assert result.name == "Ravi"
    assert result.age == 30
    assert result.gender == "Male"
    assert result.phone == "9876543210"
    assert result.address == "Hyderabad"

    query, patient_id = cursor.execute.call_args.args
    assert "WHERE patient_id = ?" in query
    assert patient_id == 1

    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_get_patient_by_id_not_found(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.fetchone.return_value = None

    result = repository.get_patient_by_id(999)

    assert result is None
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


# ---------------- UPDATE PATIENT ----------------

def test_update_patient_success(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.rowcount = 1
    patient = make_patient()

    result = repository.update_patient(patient)

    assert result is True

    query, *values = cursor.execute.call_args.args

    assert "UPDATE patients" in query
    assert values == [
        patient.name,
        patient.age,
        patient.gender,
        patient.phone,
        patient.address,
        patient.patient_id
    ]

    connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_update_patient_not_found(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.rowcount = 0

    result = repository.update_patient(make_patient(999))

    assert result is False
    connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


# ---------------- DELETE PATIENT ----------------

def test_delete_patient_success(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.rowcount = 1

    result = repository.delete_patient(1)

    assert result is True

    query, patient_id = cursor.execute.call_args.args

    assert "DELETE FROM patients" in query
    assert "WHERE patient_id = ?" in query
    assert patient_id == 1

    connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_delete_patient_not_found(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.rowcount = 0

    result = repository.delete_patient(999)

    assert result is False
    connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()

