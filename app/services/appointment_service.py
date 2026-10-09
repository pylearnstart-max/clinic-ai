from datetime import date, datetime, time

from app.models.appointment import Appointment
from app.repositories.appointment_repository import AppointmentRepository
from app.db import get_connection


class AppointmentService:

    def __init__(self):
        self.repository = AppointmentRepository()

    def add_appointment(
        self,
        patient_id,
        doctor_id,
        appointment_date,
        appointment_time,
        reason=None
    ):
        if not isinstance(patient_id, int) or isinstance(patient_id, bool) or patient_id <= 0:
            raise ValueError("Patient ID must be a positive integer")

        if not isinstance(doctor_id, int) or isinstance(doctor_id, bool) or doctor_id <= 0:
            raise ValueError("Doctor ID must be a positive integer")

        try:
            if isinstance(appointment_date, date):
                booking_date = appointment_date
            else:
                booking_date = date.fromisoformat(appointment_date)

            if isinstance(appointment_time, time):
                booking_time = appointment_time
            else:
                booking_time = time.fromisoformat(appointment_time)
        except (ValueError, TypeError):
            raise ValueError("Use date YYYY-MM-DD and time HH:MM")

        if booking_date < date.today():
            raise ValueError("Appointment date cannot be in the past")

        if booking_time.second != 0 or booking_time.microsecond != 0:
            raise ValueError("Appointment time must use whole minutes")

        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT patient_id FROM patients WHERE patient_id = ?",
                (patient_id,)
            )
            if cursor.fetchone() is None:
                raise ValueError("Patient not found")

            cursor.execute(
                "SELECT doctor_id, is_available FROM doctors WHERE doctor_id = ?",
                (doctor_id,)
            )
            doctor = cursor.fetchone()

            if doctor is None:
                raise ValueError("Doctor not found")

            if not doctor[1]:
                raise ValueError("Doctor is not available")

            cursor.execute("""
                SELECT COUNT(*)
                FROM appointments
                WHERE doctor_id = ?
                  AND appointment_date = ?
                  AND appointment_time = ?
                  AND status = 'Scheduled'
            """, (doctor_id, booking_date, booking_time))

            if cursor.fetchone()[0] > 0:
                raise ValueError("Doctor already has an appointment at this time")

        finally:
            conn.close()

        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=booking_date,
            appointment_time=booking_time,
            reason=reason,
            status="Scheduled"
        )

        return self.repository.add_appointment(appointment)

    def get_all_appointments(self):
        return self.repository.get_all_appointments()

    def update_appointment(self, appointment_id, data):
        appointments = self.get_all_appointments()

        appointment = next(
            (a for a in appointments if a.appointment_id == appointment_id),
            None
        )

        if appointment is None:
            raise ValueError("Appointment not found")

        if appointment.status == "Completed":
            raise ValueError("Completed appointments cannot be updated")

        allowed_fields = {
            "appointment_date", "appointment_time", "reason", "status"
        }

        if not data or not set(data).issubset(allowed_fields):
            raise ValueError("Provide valid appointment fields")

        if "appointment_date" in data:
            try:
                new_date = date.fromisoformat(data["appointment_date"])
            except (TypeError, ValueError):
                raise ValueError("Date must use YYYY-MM-DD format")

            if new_date < date.today():
                raise ValueError("Appointment date cannot be in the past")

            appointment.appointment_date = new_date

        if "appointment_time" in data:
            try:
                new_time = time.fromisoformat(data["appointment_time"])
            except (TypeError, ValueError):
                raise ValueError("Time must use HH:MM format")

            if new_time.second != 0 or new_time.microsecond != 0:
                raise ValueError("Time must use HH:MM format")

            appointment.appointment_time = new_time

        if "reason" in data:
            reason = data["reason"]
            if reason is not None and not isinstance(reason, str):
                raise ValueError("Reason must be text or null")
            appointment.reason = reason

        if "status" in data:
            if data["status"] not in ("Scheduled", "Completed", "Cancelled"):
                raise ValueError(
                    "Status must be Scheduled, Completed, or Cancelled"
                )
            appointment.status = data["status"]

        if appointment.status == "Scheduled":
            if self.repository.has_time_conflict(
                appointment.doctor_id,
                appointment.appointment_date,
                appointment.appointment_time,
                exclude_appointment_id=appointment_id
            ):
                raise ValueError(
                    "Doctor already has an appointment at this time"
                )

        repository = AppointmentRepository()
        updated = repository.update_appointment(appointment)

        if not updated:
            raise ValueError("Appointment update failed")

        return appointment


    def delete_appointment(self, appointment_id):
        appointments = self.get_all_appointments()

        appointment = next(
            (a for a in appointments if a.appointment_id == appointment_id),
            None
        )

        if appointment is None:
            raise ValueError("Appointment not found")

        if appointment.status == "Completed":
            raise ValueError("Completed appointments cannot be deleted")

        deleted = self.repository.delete_appointment(appointment_id)

        if not deleted:
            raise ValueError("Appointment could not be deleted")

        return True




