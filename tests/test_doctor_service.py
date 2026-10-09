
import pytest
from unittest.mock import Mock

from app.models.doctor import Doctor
from app.services.doctor_service import DoctorService


@pytest.fixture
def service():
    doctor_service = DoctorService()
    doctor_service.repository = Mock()
    return doctor_service


# ---------------- ADD DOCTOR TESTS ----------------

def test_add_doctor_success(service):
    service.repository.add_doctor.return_value = True

    result = service.add_doctor(
        name=" Dr. Ravi ",
        specialization=" Cardiology ",
        phone="9876543210",
        email="ravi@example.com",
        consultation_fee=500
    )

    assert result is True
    service.repository.add_doctor.assert_called_once()

    doctor = service.repository.add_doctor.call_args[0][0]

    assert isinstance(doctor, Doctor)
    assert doctor.name == "Dr. Ravi"
    assert doctor.specialization == "Cardiology"
    assert doctor.phone == "9876543210"
    assert doctor.email == "ravi@example.com"
    assert doctor.consultation_fee == 500
    assert doctor.is_available is True


def test_add_doctor_default_values(service):
    service.repository.add_doctor.return_value = True

    result = service.add_doctor(
        name="Dr. Ravi",
        specialization="Cardiology"
    )

    assert result is True

    doctor = service.repository.add_doctor.call_args[0][0]
    assert doctor.phone is None
    assert doctor.email is None
    assert doctor.consultation_fee == 0
    assert doctor.is_available is True


@pytest.mark.parametrize("name", ["", " ", None])
def test_add_doctor_invalid_name(service, name):
    with pytest.raises(
        ValueError,
        match="Doctor name is required"
    ):
        service.add_doctor(
            name=name,
            specialization="Cardiology"
        )

    service.repository.add_doctor.assert_not_called()


@pytest.mark.parametrize(
    "specialization",
    ["", " ", None]
)
def test_add_doctor_invalid_specialization(
    service, specialization
):
    with pytest.raises(
        ValueError,
        match="Specialization is required"
    ):
        service.add_doctor(
            name="Dr. Ravi",
            specialization=specialization
        )

    service.repository.add_doctor.assert_not_called()


@pytest.mark.parametrize(
    "fee",
    [-1, -100, True, False, "500", None, 5.5 + 0j]
)
def test_add_doctor_invalid_consultation_fee(service, fee):
    with pytest.raises(
        ValueError,
        match="Consultation fee must be a non-negative number"
    ):
        service.add_doctor(
            name="Dr. Ravi",
            specialization="Cardiology",
            consultation_fee=fee
        )

    service.repository.add_doctor.assert_not_called()


def test_add_doctor_zero_consultation_fee(service):
    service.repository.add_doctor.return_value = True

    result = service.add_doctor(
        name="Dr. Ravi",
        specialization="Cardiology",
        consultation_fee=0
    )

    assert result is True


def test_add_doctor_float_consultation_fee(service):
    service.repository.add_doctor.return_value = True

    result = service.add_doctor(
        name="Dr. Ravi",
        specialization="Cardiology",
        consultation_fee=250.50
    )

    assert result is True

    doctor = service.repository.add_doctor.call_args[0][0]
    assert doctor.consultation_fee == 250.50


# ---------------- GET ALL DOCTORS TESTS ----------------

def test_get_all_doctors_success(service):
    doctors = [
        Doctor(
            doctor_id=1,
            name="Dr. Ravi",
            specialization="Cardiology",
            consultation_fee=500
        ),
        Doctor(
            doctor_id=2,
            name="Dr. Sita",
            specialization="Dermatology",
            consultation_fee=300
        )
    ]

    service.repository.get_all_doctors.return_value = doctors

    result = service.get_all_doctors()

    assert len(result) == 2
    assert result[0].name == "Dr. Ravi"
    assert result[1].name == "Dr. Sita"
    service.repository.get_all_doctors.assert_called_once()


def test_get_all_doctors_empty(service):
    service.repository.get_all_doctors.return_value = []

    result = service.get_all_doctors()

    assert result == []


# ---------------- GET DOCTOR BY ID TESTS ----------------

def test_get_doctor_by_id_success(service):
    doctor = Doctor(
        doctor_id=10,
        name="Dr. Ravi",
        specialization="Cardiology",
        consultation_fee=500
    )

    service.repository.get_doctor_by_id.return_value = doctor

    result = service.get_doctor_by_id(10)

    assert result.doctor_id == 10
    assert result.name == "Dr. Ravi"
    service.repository.get_doctor_by_id.assert_called_once_with(10)


@pytest.mark.parametrize("doctor_id", [0, -1, -10])
def test_get_doctor_by_id_invalid_id(service, doctor_id):
    with pytest.raises(
        ValueError,
        match="Doctor ID must be positive"
    ):
        service.get_doctor_by_id(doctor_id)

    service.repository.get_doctor_by_id.assert_not_called()


def test_get_doctor_by_id_not_found(service):
    service.repository.get_doctor_by_id.return_value = None

    result = service.get_doctor_by_id(999)

    assert result is None


# ---------------- UPDATE DOCTOR TESTS ----------------

def test_update_doctor_success(service):
    service.repository.update_doctor.return_value = True

    result = service.update_doctor(
        doctor_id=10,
        name=" Dr. Ravi ",
        specialization=" Cardiology ",
        phone="9876543210",
        email="ravi@example.com",
        consultation_fee=600,
        is_available=False
    )

    assert result is True
    service.repository.update_doctor.assert_called_once()

    doctor = service.repository.update_doctor.call_args[0][0]

    assert isinstance(doctor, Doctor)
    assert doctor.doctor_id == 10
    assert doctor.name == "Dr. Ravi"
    assert doctor.specialization == "Cardiology"
    assert doctor.consultation_fee == 600
    assert doctor.is_available is False


def test_update_doctor_default_values(service):
    service.repository.update_doctor.return_value = True

    result = service.update_doctor(
        doctor_id=10,
        name="Dr. Ravi",
        specialization="Cardiology"
    )

    assert result is True

    doctor = service.repository.update_doctor.call_args[0][0]
    assert doctor.phone is None
    assert doctor.email is None
    assert doctor.consultation_fee == 0
    assert doctor.is_available is True


def test_update_doctor_invalid_id(service):
    with pytest.raises(
        ValueError,
        match="Doctor ID must be positive"
    ):
        service.update_doctor(
            doctor_id=0,
            name="Dr. Ravi",
            specialization="Cardiology"
        )

    service.repository.update_doctor.assert_not_called()


@pytest.mark.parametrize("name", ["", " ", None])
def test_update_doctor_invalid_name(service, name):
    with pytest.raises(
        ValueError,
        match="Doctor name is required"
    ):
        service.update_doctor(
            doctor_id=10,
            name=name,
            specialization="Cardiology"
        )

    service.repository.update_doctor.assert_not_called()


@pytest.mark.parametrize(
    "specialization",
    ["", " ", None]
)
def test_update_doctor_invalid_specialization(
    service, specialization
):
    with pytest.raises(
        ValueError,
        match="Specialization is required"
    ):
        service.update_doctor(
            doctor_id=10,
            name="Dr. Ravi",
            specialization=specialization
        )

    service.repository.update_doctor.assert_not_called()


@pytest.mark.parametrize(
    "fee",
    [-1, -100, True, False, "500", None, 5.5 + 0j]
)
def test_update_doctor_invalid_consultation_fee(service, fee):
    with pytest.raises(
        ValueError,
        match="Consultation fee must be a non-negative number"
    ):
        service.update_doctor(
            doctor_id=10,
            name="Dr. Ravi",
            specialization="Cardiology",
            consultation_fee=fee
        )

    service.repository.update_doctor.assert_not_called()


# ---------------- DELETE DOCTOR TESTS ----------------

def test_delete_doctor_success(service):
    service.repository.delete_doctor.return_value = True

    result = service.delete_doctor(10)

    assert result is True
    service.repository.delete_doctor.assert_called_once_with(10)


@pytest.mark.parametrize("doctor_id", [0, -1, -10])
def test_delete_doctor_invalid_id(service, doctor_id):
    with pytest.raises(
        ValueError,
        match="Doctor ID must be positive"
    ):
        service.delete_doctor(doctor_id)

    service.repository.delete_doctor.assert_not_called()


def test_delete_doctor_not_found(service):
    service.repository.delete_doctor.return_value = False

    result = service.delete_doctor(999)

    assert result is False