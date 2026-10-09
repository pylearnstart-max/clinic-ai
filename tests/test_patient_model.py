
from app.models.patient import Patient


def test_patient_str():
    patient = Patient(
        patient_id=1,
        name="Sita",
        age=30,
        gender="Female",
        phone="9876543210",
        address="Mancherial"
    )

    result = str(patient)

    assert result == "Patient(1, Sita, 9876543210)"