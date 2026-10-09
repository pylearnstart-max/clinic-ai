class Patient:

    def __init__(
        self,
        name,
        age,
        gender,
        phone,
        address,
        patient_id=None
    ):
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.gender = gender
        self.phone = phone
        self.address = address

    def __str__(self):
        return f"Patient({self.patient_id}, {self.name}, {self.phone})"