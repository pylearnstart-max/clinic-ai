
from unittest.mock import Mock

import pytest

from app.models.doctor import Doctor
from app.repositories.doctor_repository import DoctorRepository


@pytest.fixture
def setup_repository(monkeypatch):
    import app.repositories.doctor_repository as module

    cursor = Mock()
    connection = Mock()
    connection.cursor.return_value = cursor

    monkeypatch.setattr(
        module,
        "get_connection",
        lambda: connection
    )

    repository = DoctorRepository()

    return repository, cursor, connection


def make_doctor(doctor_id=1):
    return Doctor(
        doctor_id=doctor_id,
        name="Dr. Ravi",
        specialization="Cardiology",
        phone="9876543210",
        email="ravi@example.com",
        consultation_fee=500,
        is_available=True
    )


# ---------------- ADD DOCTOR ----------------

def test_add_doctor_success(setup_repository):
    repository, cursor, connection = setup_repository
    doctor = make_doctor()

    result = repository.add_doctor(doctor)

    assert result is True

    query, values = cursor.execute.call_args.args

    assert "INSERT INTO doctors" in query
    assert values == (
        doctor.name,
        doctor.specialization,
        doctor.phone,
        doctor.email,
        doctor.consultation_fee,
        doctor.is_available
    )

    connection.commit.assert_called_once()
    connection.close.assert_called_once()


def test_add_doctor_closes_connection_on_error(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.execute.side_effect = RuntimeError("Database error")

    with pytest.raises(RuntimeError, match="Database error"):
        repository.add_doctor(make_doctor())

    connection.close.assert_called_once()


# ---------------- GET ALL DOCTORS ----------------

def test_get_all_doctors_success(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.fetchall.return_value = [
        (1, "Dr. Ravi", "Cardiology", "9876543210",
         "ravi@example.com", 500, 1),
        (2, "Dr. Sita", "Dermatology", "9123456780",
         "sita@example.com", 700, 0)
    ]

    result = repository.get_all_doctors()

    assert len(result) == 2
    assert all(isinstance(doctor, Doctor) for doctor in result)

    assert result[0].doctor_id == 1
    assert result[0].name == "Dr. Ravi"
    assert result[0].specialization == "Cardiology"
    assert result[0].consultation_fee == 500
    assert result[0].is_available is True

    assert result[1].doctor_id == 2
    assert result[1].name == "Dr. Sita"
    assert result[1].is_available is False

    query = cursor.execute.call_args.args[0]
    assert "ORDER BY doctor_id" in query
    connection.close.assert_called_once()


def test_get_all_doctors_empty(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.fetchall.return_value = []

    result = repository.get_all_doctors()

    assert result == []
    connection.close.assert_called_once()


# ---------------- GET DOCTOR BY ID ----------------

def test_get_doctor_by_id_success(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.fetchone.return_value = (
        1, "Dr. Ravi", "Cardiology", "9876543210",
        "ravi@example.com", 500, 1
    )

    result = repository.get_doctor_by_id(1)

    assert isinstance(result, Doctor)
    assert result.doctor_id == 1
    assert result.name == "Dr. Ravi"
    assert result.specialization == "Cardiology"
    assert result.phone == "9876543210"
    assert result.email == "ravi@example.com"
    assert result.consultation_fee == 500
    assert result.is_available is True

    query, params = cursor.execute.call_args.args
    assert "WHERE doctor_id = ?" in query
    assert params == (1,)
    connection.close.assert_called_once()


def test_get_doctor_by_id_not_found(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.fetchone.return_value = None

    result = repository.get_doctor_by_id(999)

    assert result is None
    connection.close.assert_called_once()


# ---------------- UPDATE DOCTOR ----------------

def test_update_doctor_success(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.rowcount = 1
    doctor = make_doctor()

    result = repository.update_doctor(doctor)

    assert result is True

    query, values = cursor.execute.call_args.args

    assert "UPDATE doctors" in query
    assert values == (
        doctor.name,
        doctor.specialization,
        doctor.phone,
        doctor.email,
        doctor.consultation_fee,
        doctor.is_available,
        doctor.doctor_id
    )

    connection.commit.assert_called_once()
    connection.close.assert_called_once()


def test_update_doctor_not_found(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.rowcount = 0

    result = repository.update_doctor(make_doctor(999))

    assert result is False
    connection.commit.assert_called_once()
    connection.close.assert_called_once()


# ---------------- DELETE DOCTOR ----------------

def test_delete_doctor_success(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.rowcount = 1

    result = repository.delete_doctor(1)

    assert result is True

    query, params = cursor.execute.call_args.args
    assert "DELETE FROM doctors" in query
    assert params == (1,)

    connection.commit.assert_called_once()
    connection.close.assert_called_once()


def test_delete_doctor_not_found(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.rowcount = 0

    result = repository.delete_doctor(999)

    assert result is False
    connection.commit.assert_called_once()
    connection.close.assert_called_once()

