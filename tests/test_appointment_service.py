
from datetime import date, time, timedelta
from unittest.mock import Mock

import pytest

from app.models.appointment import Appointment
from app.services.appointment_service import AppointmentService


# ---------------- TEST SETUP ----------------

class FakeCursor:
    def __init__(self, results):
        self.results = iter(results)
        self.executed_queries = []

    def execute(self, query, params=None):
        self.executed_queries.append((query, params))
        return self

    def fetchone(self):
        return next(self.results, None)


class FakeConnection:
    def __init__(self, results):
        self.fake_cursor = FakeCursor(results)
        self.closed = False

    def cursor(self):
        return self.fake_cursor

    def close(self):
        self.closed = True


@pytest.fixture
def service(monkeypatch):
    import app.services.appointment_service as service_module

    repository = Mock()
    monkeypatch.setattr(
        service_module,
        "AppointmentRepository",
        lambda: repository
    )

    appointment_service = AppointmentService()
    appointment_service.repository = repository

    return appointment_service


def create_appointment(
    appointment_id=101,
    appointment_date=None,
    appointment_time=None,
    reason="General checkup",
    status="Scheduled"
):
    return Appointment(
        appointment_id=appointment_id,
        patient_id=1,
        doctor_id=2,
        appointment_date=(
            appointment_date or date.today() + timedelta(days=1)
        ),
        appointment_time=appointment_time or time(10, 30),
        reason=reason,
        status=status
    )


def valid_booking_results():
    return [(1,), (2, True), (0,)]


# ---------------- ADD APPOINTMENT TESTS ----------------

def test_add_appointment_success(service, monkeypatch):
    import app.services.appointment_service as service_module

    connection = FakeConnection(valid_booking_results())
    monkeypatch.setattr(
        service_module,
        "get_connection",
        lambda: connection
    )

    service.repository.add_appointment.return_value = "saved"

    result = service.add_appointment(
        patient_id=1,
        doctor_id=2,
        appointment_date=(
            date.today() + timedelta(days=1)
        ).isoformat(),
        appointment_time="10:30",
        reason="General checkup"
    )

    assert result == "saved"
    service.repository.add_appointment.assert_called_once()

    appointment = service.repository.add_appointment.call_args[0][0]

    assert isinstance(appointment, Appointment)
    assert appointment.patient_id == 1
    assert appointment.doctor_id == 2
    assert appointment.appointment_time == time(10, 30)
    assert appointment.reason == "General checkup"
    assert appointment.status == "Scheduled"
    assert connection.closed is True


@pytest.mark.parametrize("patient_id", [0, -1, True, "1", None])
def test_add_appointment_invalid_patient_id(service, patient_id):
    with pytest.raises(
        ValueError,
        match="Patient ID must be a positive integer"
    ):
        service.add_appointment(
            patient_id=patient_id,
            doctor_id=2,
            appointment_date=(
                date.today() + timedelta(days=1)
            ).isoformat(),
            appointment_time="10:30"
        )


@pytest.mark.parametrize("doctor_id", [0, -1, True, "2", None])
def test_add_appointment_invalid_doctor_id(service, doctor_id):
    with pytest.raises(
        ValueError,
        match="Doctor ID must be a positive integer"
    ):
        service.add_appointment(
            patient_id=1,
            doctor_id=doctor_id,
            appointment_date=(
                date.today() + timedelta(days=1)
            ).isoformat(),
            appointment_time="10:30"
        )


@pytest.mark.parametrize(
    "booking_date, booking_time",
    [
        ("invalid-date", "10:30"),
        ((date.today() + timedelta(days=1)).isoformat(), "invalid-time"),
        (None, "10:30"),
        ((date.today() + timedelta(days=1)).isoformat(), None),
    ]
)
def test_add_appointment_invalid_date_or_time(
    service, booking_date, booking_time
):
    with pytest.raises(
        ValueError,
        match="Use date YYYY-MM-DD and time HH:MM"
    ):
        service.add_appointment(
            patient_id=1,
            doctor_id=2,
            appointment_date=booking_date,
            appointment_time=booking_time
        )


def test_add_appointment_past_date(service):
    past_date = (date.today() - timedelta(days=1)).isoformat()

    with pytest.raises(
        ValueError,
        match="Appointment date cannot be in the past"
    ):
        service.add_appointment(
            patient_id=1,
            doctor_id=2,
            appointment_date=past_date,
            appointment_time="10:30"
        )


def test_add_appointment_time_with_seconds_rejected(service):
    with pytest.raises(
        ValueError,
        match="Appointment time must use whole minutes"
    ):
        service.add_appointment(
            patient_id=1,
            doctor_id=2,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=time(10, 30, 15)
        )


def test_add_appointment_patient_not_found(service, monkeypatch):
    import app.services.appointment_service as service_module

    # Patient query returns None: patient does not exist.
    connection = FakeConnection([None])
    monkeypatch.setattr(
        service_module,
        "get_connection",
        lambda: connection
    )

    with pytest.raises(ValueError, match="Patient not found"):
        service.add_appointment(
            patient_id=1,
            doctor_id=2,
            appointment_date=(
                date.today() + timedelta(days=1)
            ).isoformat(),
            appointment_time="10:30"
        )

    assert connection.closed is True
    service.repository.add_appointment.assert_not_called()


def test_add_appointment_doctor_not_found(service, monkeypatch):
    import app.services.appointment_service as service_module

    # Patient exists; doctor query returns None.
    connection = FakeConnection([(1,), None])
    monkeypatch.setattr(
        service_module,
        "get_connection",
        lambda: connection
    )

    with pytest.raises(ValueError, match="Doctor not found"):
        service.add_appointment(
            patient_id=1,
            doctor_id=2,
            appointment_date=(
                date.today() + timedelta(days=1)
            ).isoformat(),
            appointment_time="10:30"
        )

    assert connection.closed is True
    service.repository.add_appointment.assert_not_called()


def test_add_appointment_doctor_unavailable(service, monkeypatch):
    import app.services.appointment_service as service_module

    connection = FakeConnection([(1,), (2, False)])
    monkeypatch.setattr(
        service_module,
        "get_connection",
        lambda: connection
    )

    with pytest.raises(ValueError, match="Doctor is not available"):
        service.add_appointment(
            patient_id=1,
            doctor_id=2,
            appointment_date=(
                date.today() + timedelta(days=1)
            ).isoformat(),
            appointment_time="10:30"
        )

    assert connection.closed is True
    service.repository.add_appointment.assert_not_called()


def test_add_appointment_time_conflict(service, monkeypatch):
    import app.services.appointment_service as service_module

    connection = FakeConnection([(1,), (2, True), (1,)])
    monkeypatch.setattr(
        service_module,
        "get_connection",
        lambda: connection
    )

    with pytest.raises(
        ValueError,
        match="Doctor already has an appointment at this time"
    ):
        service.add_appointment(
            patient_id=1,
            doctor_id=2,
            appointment_date=(
                date.today() + timedelta(days=1)
            ).isoformat(),
            appointment_time="10:30"
        )

    assert connection.closed is True
    service.repository.add_appointment.assert_not_called()


# ---------------- GET APPOINTMENTS TESTS ----------------

def test_get_all_appointments_success(service):
    appointments = [
        create_appointment(),
        create_appointment(appointment_id=102)
    ]
    service.repository.get_all_appointments.return_value = appointments

    result = service.get_all_appointments()

    assert result == appointments
    service.repository.get_all_appointments.assert_called_once()


def test_get_all_appointments_empty(service):
    service.repository.get_all_appointments.return_value = []

    result = service.get_all_appointments()

    assert result == []


# ---------------- UPDATE APPOINTMENT TESTS ----------------

def test_update_appointment_success(service, monkeypatch):
    import app.services.appointment_service as service_module

    appointment = create_appointment()
    service.repository.get_all_appointments.return_value = [appointment]
    service.repository.has_time_conflict.return_value = False

    # update_appointment creates a new AppointmentRepository.
    monkeypatch.setattr(
        service_module,
        "AppointmentRepository",
        lambda: service.repository
    )
    service.repository.update_appointment.return_value = True

    result = service.update_appointment(
        101,
        {
            "reason": "Follow-up checkup",
            "appointment_time": "11:30"
        }
    )

    assert result.reason == "Follow-up checkup"
    assert result.appointment_time == time(11, 30)
    service.repository.has_time_conflict.assert_called_once()
    service.repository.update_appointment.assert_called_once_with(appointment)


def test_update_appointment_not_found(service):
    service.repository.get_all_appointments.return_value = []

    with pytest.raises(ValueError, match="Appointment not found"):
        service.update_appointment(999, {"reason": "Checkup"})


def test_update_completed_appointment_rejected(service):
    appointment = create_appointment(status="Completed")
    service.repository.get_all_appointments.return_value = [appointment]

    with pytest.raises(
        ValueError,
        match="Completed appointments cannot be updated"
    ):
        service.update_appointment(101, {"reason": "Updated reason"})


@pytest.mark.parametrize(
    "data",
    [{}, {"invalid_field": "value"}, None]
)
def test_update_invalid_fields(service, data):
    service.repository.get_all_appointments.return_value = [
        create_appointment()
    ]

    with pytest.raises(
        ValueError,
        match="Provide valid appointment fields"
    ):
        service.update_appointment(101, data)


def test_update_appointment_invalid_date_format(service):
    service.repository.get_all_appointments.return_value = [
        create_appointment()
    ]

    with pytest.raises(
        ValueError,
        match="Date must use YYYY-MM-DD format"
    ):
        service.update_appointment(
            101,
            {"appointment_date": "not-a-date"}
        )


def test_update_appointment_past_date(service):
    service.repository.get_all_appointments.return_value = [
        create_appointment()
    ]
    past_date = (date.today() - timedelta(days=1)).isoformat()

    with pytest.raises(
        ValueError,
        match="Appointment date cannot be in the past"
    ):
        service.update_appointment(
            101,
            {"appointment_date": past_date}
        )


def test_update_appointment_invalid_time_format(service):
    service.repository.get_all_appointments.return_value = [
        create_appointment()
    ]

    with pytest.raises(
        ValueError,
        match="Time must use HH:MM format"
    ):
        service.update_appointment(
            101,
            {"appointment_time": "bad-time"}
        )


def test_update_appointment_time_with_seconds_rejected(service):
    service.repository.get_all_appointments.return_value = [
        create_appointment()
    ]

    with pytest.raises(
        ValueError,
        match="Time must use HH:MM format"
    ):
        service.update_appointment(
            101,
            {"appointment_time": "10:30:15"}
        )


@pytest.mark.parametrize("reason", [123, [], {}])
def test_update_appointment_invalid_reason(service, reason):
    service.repository.get_all_appointments.return_value = [
        create_appointment()
    ]

    with pytest.raises(ValueError, match="Reason must be text or null"):
        service.update_appointment(101, {"reason": reason})


@pytest.mark.parametrize("status", ["Unknown", "", None, 123])
def test_update_appointment_invalid_status(service, status):
    service.repository.get_all_appointments.return_value = [
        create_appointment()
    ]

    with pytest.raises(
        ValueError,
        match="Status must be Scheduled, Completed, or Cancelled"
    ):
        service.update_appointment(101, {"status": status})


def test_update_appointment_time_conflict(service):
    service.repository.get_all_appointments.return_value = [
        create_appointment()
    ]
    service.repository.has_time_conflict.return_value = True

    with pytest.raises(
        ValueError,
        match="Doctor already has an appointment at this time"
    ):
        service.update_appointment(101, {"reason": "Updated reason"})

    service.repository.update_appointment.assert_not_called()


def test_update_appointment_repository_failure(service, monkeypatch):
    import app.services.appointment_service as service_module

    service.repository.get_all_appointments.return_value = [
        create_appointment()
    ]
    service.repository.has_time_conflict.return_value = False
    service.repository.update_appointment.return_value = False

    monkeypatch.setattr(
        service_module,
        "AppointmentRepository",
        lambda: service.repository
    )

    with pytest.raises(
        ValueError,
        match="Appointment update failed"
    ):
        service.update_appointment(101, {"reason": "Updated reason"})


def test_update_appointment_cancelled_skips_conflict_check(
    service, monkeypatch
):
    import app.services.appointment_service as service_module

    appointment = create_appointment()
    service.repository.get_all_appointments.return_value = [appointment]
    service.repository.update_appointment.return_value = True

    monkeypatch.setattr(
        service_module,
        "AppointmentRepository",
        lambda: service.repository
    )

    result = service.update_appointment(101, {"status": "Cancelled"})

    assert result.status == "Cancelled"
    service.repository.has_time_conflict.assert_not_called()


# ---------------- DELETE APPOINTMENT TESTS ----------------

def test_delete_appointment_success(service):
    service.repository.get_all_appointments.return_value = [
        create_appointment()
    ]
    service.repository.delete_appointment.return_value = True

    result = service.delete_appointment(101)

    assert result is True
    service.repository.delete_appointment.assert_called_once_with(101)


def test_delete_appointment_not_found(service):
    service.repository.get_all_appointments.return_value = []

    with pytest.raises(ValueError, match="Appointment not found"):
        service.delete_appointment(999)


def test_delete_completed_appointment_rejected(service):
    appointment = create_appointment(status="Completed")
    service.repository.get_all_appointments.return_value = [appointment]

    with pytest.raises(
        ValueError,
        match="Completed appointments cannot be deleted"
    ):
        service.delete_appointment(101)

    service.repository.delete_appointment.assert_not_called()


def test_delete_appointment_repository_failure(service):
    service.repository.get_all_appointments.return_value = [
        create_appointment()
    ]
    service.repository.delete_appointment.return_value = False

    with pytest.raises(
        ValueError,
        match="Appointment could not be deleted"
    ):
        service.delete_appointment(101)

def test_update_appointment_updates_date(monkeypatch):
    from datetime import date, time, timedelta

    from app.services.appointment_service import AppointmentService
    from app.models.appointment import Appointment

    service = AppointmentService()

    appointment = Appointment(
        appointment_id=1,
        patient_id=10,
        doctor_id=20,
        appointment_date=date.today() + timedelta(days=2),
        appointment_time=time(10, 30),
        reason="Checkup",
        status="Scheduled"
    )

    monkeypatch.setattr(
        service,
        "get_all_appointments",
        lambda: [appointment]
    )

    monkeypatch.setattr(
        service.repository,
        "has_time_conflict",
        lambda *args, **kwargs: False
    )

    monkeypatch.setattr(
        "app.services.appointment_service.AppointmentRepository",
        lambda: type(
            "FakeRepository",
            (),
            {"update_appointment": lambda self, item: True}
        )()
    )

    new_date = date.today() + timedelta(days=7)

    result = service.update_appointment(
        1,
        {"appointment_date": new_date.isoformat()}
    )

    assert result.appointment_date == new_date