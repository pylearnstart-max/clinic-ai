
from app.exceptions.custom_exceptions import ValidationError
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
            raise ValidationError("Patient name is required")

        if age is not None and age <= 0:
            raise ValidationError("Age must be greater than 0")

        if not phone:
            raise ValidationError("Phone number is required")

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

    def search_patients(
        self,
        search=None,
        min_age=None,
        max_age=None,
        page=1,
        per_page=10
    ):
        if page < 1:
            raise ValidationError("Page must be greater than 0")

        if per_page < 1 or per_page > 100:
            raise ValidationError(
                "per_page must be between 1 and 100"
            )

        if min_age is not None and min_age < 0:
            raise ValidationError("min_age cannot be negative")

        if max_age is not None and max_age < 0:
            raise ValidationError("max_age cannot be negative")

        if (
            min_age is not None
            and max_age is not None
            and min_age > max_age
        ):
            raise ValidationError(
                "min_age cannot be greater than max_age"
            )

        return self.repository.search_patients(
            search=search,
            min_age=min_age,
            max_age=max_age,
            page=page,
            per_page=per_page
        )

    def get_patient_by_id(self, patient_id):
        if patient_id <= 0:
            raise ValidationError(
                "Patient ID must be greater than 0"
            )

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
            raise ValidationError(
                "Patient ID must be greater than 0"
            )

        if not name:
            raise ValidationError("Patient name is required")

        if age is not None and age <= 0:
            raise ValidationError("Age must be greater than 0")

        if not phone:
            raise ValidationError("Phone number is required")

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
            raise ValidationError(
                "Patient ID must be greater than 0"
            )

        return self.repository.delete_patient(patient_id)