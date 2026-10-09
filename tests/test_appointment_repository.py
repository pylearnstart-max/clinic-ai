
from datetime import date, time
from unittest.mock import Mock

import pytest

from app.models.appointment import Appointment
from app.repositories.appointment_repository import AppointmentRepository


# ---------------- TEST SETUP ----------------

class FakeCursor:
    def __init__(
        self,
        one_result=None,
        all_results=None,
        rowcount=1
    ):
        self.one_result = one_result
        self.all_results = all_results or []
        self.rowcount = rowcount
        self.executed_queries = []

    def execute(self, query, *params):
        self.executed_queries.append((query, params))
        return self

    def fetchone(self):
        return self.one_result

    def fetchall(self):
        return self.all_results


class FakeConnection:
    def __init__(self, cursor):
        self.fake_cursor = cursor
        self.committed = False
        self.closed = False

    def cursor(self):
        return self.fake_cursor

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


@pytest.fixture
def setup_repository(monkeypatch):
    import app.repositories.appointment_repository as repository_module

    cursor = FakeCursor()
    connection = FakeConnection(cursor)

    monkeypatch.setattr(
        repository_module,
        "get_connection",
        lambda: connection
    )

    repository = AppointmentRepository()

    return repository, cursor, connection


def make_appointment():
    return Appointment(
        appointment_id=101,
        patient_id=1,
        doctor_id=2,
        appointment_date=date(2026, 11, 10),
        appointment_time=time(10, 30),
        reason="General checkup",
        status="Scheduled"
    )


# ---------------- ADD APPOINTMENT ----------------

def test_add_appointment_success(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.one_result = (101,)
    appointment = make_appointment()

    result = repository.add_appointment(appointment)

    assert result is appointment
    assert result.appointment_id == 101
    assert cursor.executed_queries
    assert "INSERT INTO appointments" in cursor.executed_queries[0][0]
    assert connection.committed is True
    assert connection.closed is True


def test_add_appointment_passes_correct_values(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.one_result = (101,)
    appointment = make_appointment()

    repository.add_appointment(appointment)

    query, params = cursor.executed_queries[0]

    assert "OUTPUT INSERTED.appointment_id" in query

    values = params[0]

    assert values == (
        appointment.patient_id,
        appointment.doctor_id,
        appointment.appointment_date,
        appointment.appointment_time,
        appointment.reason,
        appointment.status
    )


# ---------------- GET ALL APPOINTMENTS ----------------

def test_get_all_appointments_success(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.all_results = [
        (
            101, 1, 2, date(2026, 11, 10),
            time(10, 30), "Checkup", "Scheduled"
        ),
        (
            102, 3, 4, date(2026, 11, 11),
            time(11, 0), "Follow-up", "Completed"
        )
    ]

    result = repository.get_all_appointments()

    assert len(result) == 2
    assert all(isinstance(item, Appointment) for item in result)

    assert result[0].appointment_id == 101
    assert result[0].patient_id == 1
    assert result[0].doctor_id == 2
    assert result[0].reason == "Checkup"
    assert result[0].status == "Scheduled"

    assert result[1].appointment_id == 102
    assert result[1].reason == "Follow-up"
    assert result[1].status == "Completed"

    query, params = cursor.executed_queries[0]
    assert "ORDER BY appointment_date, appointment_time" in query
    assert connection.closed is True


def test_get_all_appointments_empty(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.all_results = []

    result = repository.get_all_appointments()

    assert result == []
    assert connection.closed is True


# ---------------- UPDATE APPOINTMENT ----------------

def test_update_appointment_success(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.rowcount = 1
    appointment = make_appointment()

    result = repository.update_appointment(appointment)

    assert result is True

    query, params = cursor.executed_queries[0]

    assert "UPDATE appointments" in query
    assert params == (
        appointment.appointment_date,
        appointment.appointment_time,
        appointment.reason,
        appointment.status,
        appointment.appointment_id
    )

    assert connection.committed is True
    assert connection.closed is True


def test_update_appointment_not_found(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.rowcount = 0

    result = repository.update_appointment(make_appointment())

    assert result is False
    assert connection.committed is True
    assert connection.closed is True


# ---------------- DELETE APPOINTMENT ----------------

def test_delete_appointment_success(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.rowcount = 1

    result = repository.delete_appointment(101)

    assert result is True

    query, params = cursor.executed_queries[0]

    assert "DELETE FROM appointments" in query
    assert params == (101,)
    assert connection.committed is True
    assert connection.closed is True


def test_delete_appointment_not_found(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.rowcount = 0

    result = repository.delete_appointment(999)

    assert result is False
    assert connection.committed is True
    assert connection.closed is True


# ---------------- CHECK TIME CONFLICT ----------------

def test_has_time_conflict_found(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.one_result = (1,)

    result = repository.has_time_conflict(
        doctor_id=2,
        appointment_date=date(2026, 11, 10),
        appointment_time=time(10, 30)
    )

    assert result is True

    query, params = cursor.executed_queries[0]

    assert "SELECT COUNT(*)" in query
    assert "status = 'Scheduled'" in query
    assert params == (
        2,
        date(2026, 11, 10),
        time(10, 30)
    )
    assert connection.closed is True


def test_has_time_conflict_not_found(setup_repository):
    repository, cursor, connection = setup_repository

    cursor.one_result = (0,)

    result = repository.has_time_conflict(
        doctor_id=2,
        appointment_date=date(2026, 11, 10),
        appointment_time=time(10, 30)
    )

    assert result is False
    assert connection.closed is True


def test_has_time_conflict_excludes_current_appointment(
    setup_repository
):
    repository, cursor, connection = setup_repository

    cursor.one_result = (0,)

    result = repository.has_time_conflict(
        doctor_id=2,
        appointment_date=date(2026, 11, 10),
        appointment_time=time(10, 30),
        exclude_appointment_id=101
    )

    assert result is False

    query, params = cursor.executed_queries[0]

    assert "appointment_id <> ?" in query
    assert params == (
        2,
        date(2026, 11, 10),
        time(10, 30),
        101
    )
    assert connection.closed is True


# ---------------- CONNECTION CLEANUP ----------------

def test_connection_closes_when_query_raises_error(
    setup_repository
):
    repository, cursor, connection = setup_repository

    def raise_error(query, *params):
        raise RuntimeError("Database error")

    cursor.execute = raise_error

    with pytest.raises(RuntimeError, match="Database error"):
        repository.get_all_appointments()

    assert connection.closed is True

