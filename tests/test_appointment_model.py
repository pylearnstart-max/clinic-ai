
from datetime import date, time

from app.models.appointment import Appointment


def test_appointment_str():
    appointment = Appointment(
        appointment_id=1,
        patient_id=10,
        doctor_id=20,
        appointment_date=date(2026, 10, 9),
        appointment_time=time(10, 30),
        reason="Regular checkup",
        status="Scheduled"
    )

    result = str(appointment)

    assert "Appointment ID: 1" in result
    assert "Patient ID: 10" in result
    assert "Doctor ID: 20" in result
    assert "Date: 2026-10-09" in result
    assert "Time: 10:30:00" in result
    assert "Status: Scheduled" in result