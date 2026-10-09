class Doctor:
    def __init__(
        self,
        doctor_id=None,
        name=None,
        specialization=None,
        phone=None,
        email=None,
        consultation_fee=None,
        is_available=True
    ):
        self.doctor_id = doctor_id
        self.name = name
        self.specialization = specialization
        self.phone = phone
        self.email = email
        self.consultation_fee = consultation_fee
        self.is_available = is_available

    def __str__(self):
        return (
            f"Doctor ID: {self.doctor_id}, "
            f"Name: {self.name}, "
            f"Specialization: {self.specialization}"
        )
