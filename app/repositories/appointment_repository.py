from app.db import get_connection
from app.models.appointment import Appointment


class AppointmentRepository:

    def add_appointment(self, appointment):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO appointments
                (
                    patient_id,
                    doctor_id,
                    appointment_date,
                    appointment_time,
                    reason,
                    status
                )
                OUTPUT INSERTED.appointment_id
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                appointment.patient_id,
                appointment.doctor_id,
                appointment.appointment_date,
                appointment.appointment_time,
                appointment.reason,
                appointment.status
            ))

            row = cursor.fetchone()
            conn.commit()

            appointment.appointment_id = row[0]
            return appointment

        finally:
            conn.close()

    def get_all_appointments(self):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    appointment_id,
                    patient_id,
                    doctor_id,
                    appointment_date,
                    appointment_time,
                    reason,
                    status
                FROM appointments
                ORDER BY appointment_date, appointment_time
            """)

            appointments = []

            for row in cursor.fetchall():
                appointments.append(
                    Appointment(
                        appointment_id=row[0],
                        patient_id=row[1],
                        doctor_id=row[2],
                        appointment_date=row[3],
                        appointment_time=row[4],
                        reason=row[5],
                        status=row[6]
                    )
                )

            return appointments

        finally:
            conn.close()

    def update_appointment(self, appointment):
        query = """
            UPDATE appointments
            SET appointment_date = ?,
                appointment_time = ?,
                reason = ?,
                status = ?
            WHERE appointment_id = ?
        """

        connection = get_connection()

        try:
            cursor = connection.cursor()
            cursor.execute(
                query,
                appointment.appointment_date,
                appointment.appointment_time,
                appointment.reason,
                appointment.status,
                appointment.appointment_id
            )
            connection.commit()
            return cursor.rowcount > 0

        finally:
            connection.close()


    def delete_appointment(self, appointment_id):
        query = """
            DELETE FROM appointments
            WHERE appointment_id = ?
        """

        connection = get_connection()

        try:
            cursor = connection.cursor()
            cursor.execute(query, appointment_id)
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()


    def has_time_conflict(
        self, doctor_id, appointment_date, appointment_time,
        exclude_appointment_id=None
    ):
        query = """
            SELECT COUNT(*)
            FROM appointments
            WHERE doctor_id = ?
              AND appointment_date = ?
              AND appointment_time = ?
              AND status = 'Scheduled'
        """
        params = [
            doctor_id,
            appointment_date,
            appointment_time
        ]

        if exclude_appointment_id is not None:
            query += " AND appointment_id <> ?"
            params.append(exclude_appointment_id)

        connection = get_connection()

        try:
            cursor = connection.cursor()
            cursor.execute(query, *params)
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            connection.close()

