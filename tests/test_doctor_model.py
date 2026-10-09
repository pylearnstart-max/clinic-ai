
from app.models.doctor import Doctor


def test_doctor_str():
    doctor = Doctor(
        doctor_id=1,
        name="Ravi",
        specialization="Cardiology"
    )

    result = str(doctor)

    assert "Doctor ID: 1" in result
    assert "Name: Ravi" in result
    assert "Specialization: Cardiology" in result