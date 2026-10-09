from app.db import get_connection
from app.models.patient import Patient


class PatientRepository:

    def add_patient(self, patient):

        connection = get_connection()
        cursor = connection.cursor()

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

        cursor.close()
        connection.close()

        return True

    def get_all_patients(self):

        connection = get_connection()
        cursor = connection.cursor()

        query = """
        SELECT
            patient_id,
            name,
            age,
            gender,
            phone,
            address
        FROM patients
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        patients = []

        for row in rows:
            patient = Patient(
                patient_id=row[0],
                name=row[1],
                age=row[2],
                gender=row[3],
                phone=row[4],
                address=row[5]
            )

            patients.append(patient)

        cursor.close()
        connection.close()

        return patients

    def get_patient_by_id(self, patient_id):

        connection = get_connection()
        cursor = connection.cursor()

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

        cursor.close()
        connection.close()

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

    def update_patient(self, patient):

        connection = get_connection()
        cursor = connection.cursor()

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

        rows_affected = cursor.rowcount

        cursor.close()
        connection.close()

        return rows_affected > 0

    def delete_patient(self, patient_id):

        connection = get_connection()
        cursor = connection.cursor()

        query = """
        DELETE FROM patients
        WHERE patient_id = ?
        """

        cursor.execute(query, patient_id)

        connection.commit()

        rows_affected = cursor.rowcount

        cursor.close()
        connection.close()

        return rows_affected > 0
