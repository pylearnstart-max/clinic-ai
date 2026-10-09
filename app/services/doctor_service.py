from app.models.doctor import Doctor
from app.repositories.doctor_repository import DoctorRepository


class DoctorService:

    def __init__(self):
        self.repository = DoctorRepository()

    def add_doctor(
        self,
        name,
        specialization,
        phone=None,
        email=None,
        consultation_fee=0
    ):
        if not name or not name.strip():
            raise ValueError("Doctor name is required")

        if not specialization or not specialization.strip():
            raise ValueError("Specialization is required")

        if (
            isinstance(consultation_fee, bool)
            or not isinstance(consultation_fee, (int, float))
            or consultation_fee < 0
        ):
            raise ValueError("Consultation fee must be a non-negative number")

        doctor = Doctor(
            name=name.strip(),
            specialization=specialization.strip(),
            phone=phone,
            email=email,
            consultation_fee=consultation_fee,
            is_available=True
        )

        return self.repository.add_doctor(doctor)

    def get_all_doctors(self):
        return self.repository.get_all_doctors()

    def get_doctor_by_id(self, doctor_id):
        if doctor_id <= 0:
            raise ValueError("Doctor ID must be positive")

        return self.repository.get_doctor_by_id(doctor_id)

    def update_doctor(
        self,
        doctor_id,
        name,
        specialization,
        phone=None,
        email=None,
        consultation_fee=0,
        is_available=True
    ):
        if doctor_id <= 0:
            raise ValueError("Doctor ID must be positive")

        if not name or not name.strip():
            raise ValueError("Doctor name is required")

        if not specialization or not specialization.strip():
            raise ValueError("Specialization is required")

        if (
            isinstance(consultation_fee, bool)
            or not isinstance(consultation_fee, (int, float))
            or consultation_fee < 0
        ):
            raise ValueError("Consultation fee must be a non-negative number")

        doctor = Doctor(
            doctor_id=doctor_id,
            name=name.strip(),
            specialization=specialization.strip(),
            phone=phone,
            email=email,
            consultation_fee=consultation_fee,
            is_available=is_available
        )

        return self.repository.update_doctor(doctor)

    def delete_doctor(self, doctor_id):
        if doctor_id <= 0:
            raise ValueError("Doctor ID must be positive")

        return self.repository.delete_doctor(doctor_id)
