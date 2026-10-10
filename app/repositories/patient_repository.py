
from app.db import get_connection
from app.models.patient import Patient


class PatientRepository:

    def add_patient(self, patient):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            query = """
                INSERT INTO patients
                (name, age, gender, phone, address)
                VALUES (?, ?, ?, ?, ?)
            """

            cursor.execute(
                query,
                patient.name,
                patient.age,
                patient.gender,
                patient.phone,
                patient.address
            )

            connection.commit()
            return True

        finally:
            cursor.close()
            connection.close()

    def get_all_patients(self):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            query = """
                SELECT
                    patient_id,
                    name,
                    age,
                    gender,
                    phone,
                    address
                FROM patients
                ORDER BY patient_id
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            return [
                Patient(
                    patient_id=row[0],
                    name=row[1],
                    age=row[2],
                    gender=row[3],
                    phone=row[4],
                    address=row[5]
                )
                for row in rows
            ]

        finally:
            cursor.close()
            connection.close()

    def search_patients(
        self,
        search=None,
        min_age=None,
        max_age=None,
        page=1,
        per_page=10
    ):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            query = """
                SELECT
                    patient_id,
                    name,
                    age,
                    gender,
                    phone,
                    address
                FROM patients
                WHERE (? IS NULL OR name LIKE ?)
                  AND (? IS NULL OR age >= ?)
                  AND (? IS NULL OR age <= ?)
                ORDER BY patient_id
                OFFSET ? ROWS
                FETCH NEXT ? ROWS ONLY
            """

            search_value = (
                f"%{search}%" if search else None
            )

            offset = (page - 1) * per_page

            cursor.execute(
                query,
                search_value,
                search_value,
                min_age,
                min_age,
                max_age,
                max_age,
                offset,
                per_page
            )

            rows = cursor.fetchall()

            return [
                Patient(
                    patient_id=row[0],
                    name=row[1],
                    age=row[2],
                    gender=row[3],
                    phone=row[4],
                    address=row[5]
                )
                for row in rows
            ]

        finally:
            cursor.close()
            connection.close()

    def get_patient_by_id(self, patient_id):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            query = """
                SELECT
                    patient_id,
                    name,
                    age,
                    gender,
                    phone,
                    address
                FROM patients
                WHERE patient_id = ?
            """

            cursor.execute(query, patient_id)
            row = cursor.fetchone()

            if row is None:
                return None

            return Patient(
                patient_id=row[0],
                name=row[1],
                age=row[2],
                gender=row[3],
                phone=row[4],
                address=row[5]
            )

        finally:
            cursor.close()
            connection.close()

    def update_patient(self, patient):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            query = """
                UPDATE patients
                SET
                    name = ?,
                    age = ?,
                    gender = ?,
                    phone = ?,
                    address = ?
                WHERE patient_id = ?
            """

            cursor.execute(
                query,
                patient.name,
                patient.age,
                patient.gender,
                patient.phone,
                patient.address,
                patient.patient_id
            )

            connection.commit()
            return cursor.rowcount > 0

        finally:
            cursor.close()
            connection.close()

    def delete_patient(self, patient_id):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            query = """
                DELETE FROM patients
                WHERE patient_id = ?
            """

            cursor.execute(query, patient_id)
            connection.commit()

            return cursor.rowcount > 0

        finally:
            cursor.close()
            connection.close()