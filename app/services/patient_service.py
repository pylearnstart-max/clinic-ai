
from app.models.patient import Patient
from app.repositories.patient_repository import PatientRepository



class PatientService:

    def __init__(self):
        self.repository = PatientRepository()

    def add_patient(
        self,
        name,
        age,
        gender,
        phone,
        address
    ):
        if not name:
            raise ValueError("Patient name is required")

        if age is not None and age <= 0:
            raise ValueError("Age must be greater than 0")

        if not phone:
            raise ValueError("Phone number is required")

        patient = Patient(
            name=name,
            age=age,
            gender=gender,
            phone=phone,
            address=address
        )

        return self.repository.add_patient(patient)

    def get_all_patients(self):
        return self.repository.get_all_patients()

    def get_patient_by_id(self, patient_id):
        if patient_id <= 0:
            raise ValueError("Patient ID must be greater than 0")

        return self.repository.get_patient_by_id(patient_id)

    def update_patient(
        self,
        patient_id,
        name,
        age,
        gender,
        phone,
        address
    ):
        if patient_id <= 0:
            raise ValueError("Patient ID must be greater than 0")

        if not name:
            raise ValueError("Patient name is required")

        if age is not None and age <= 0:
            raise ValueError("Age must be greater than 0")

        if not phone:
            raise ValueError("Phone number is required")

        patient = Patient(
            patient_id=patient_id,
            name=name,
            age=age,
            gender=gender,
            phone=phone,
            address=address
        )

        return self.repository.update_patient(patient)

    def delete_patient(self, patient_id):
        if patient_id <= 0:
            raise ValueError("Patient ID must be greater than 0")

        return self.repository.delete_patient(patient_id)