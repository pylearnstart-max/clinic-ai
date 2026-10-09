from app.db import get_connection
from app.models.doctor import Doctor


class DoctorRepository:

    def add_doctor(self, doctor):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO doctors
                (name, specialization, phone, email,
                 consultation_fee, is_available)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                doctor.name, doctor.specialization,
                doctor.phone, doctor.email,
                doctor.consultation_fee, doctor.is_available
            ))
            conn.commit()
            return True
        finally:
            conn.close()

    def get_all_doctors(self):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT doctor_id, name, specialization,
                       phone, email, consultation_fee, is_available
                FROM doctors ORDER BY doctor_id
            """)
            return [
                Doctor(
                    doctor_id=r[0], name=r[1],
                    specialization=r[2], phone=r[3],
                    email=r[4], consultation_fee=r[5],
                    is_available=bool(r[6])
                )
                for r in cursor.fetchall()
            ]
        finally:
            conn.close()

    def get_doctor_by_id(self, doctor_id):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT doctor_id, name, specialization,
                       phone, email, consultation_fee, is_available
                FROM doctors WHERE doctor_id = ?
            """, (doctor_id,))
            r = cursor.fetchone()

            if r is None:
                return None

            return Doctor(
                doctor_id=r[0], name=r[1],
                specialization=r[2], phone=r[3],
                email=r[4], consultation_fee=r[5],
                is_available=bool(r[6])
            )
        finally:
            conn.close()

    def update_doctor(self, doctor):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE doctors
                SET name = ?, specialization = ?, phone = ?,
                    email = ?, consultation_fee = ?, is_available = ?
                WHERE doctor_id = ?
            """, (
                doctor.name, doctor.specialization,
                doctor.phone, doctor.email,
                doctor.consultation_fee, doctor.is_available,
                doctor.doctor_id
            ))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_doctor(self, doctor_id):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM doctors WHERE doctor_id = ?",
                (doctor_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
