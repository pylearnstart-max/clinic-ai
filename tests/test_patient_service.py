
import pytest
from unittest.mock import Mock

from app.models.patient import Patient
from app.services.patient_service import PatientService


@pytest.fixture
def service():
    patient_service = PatientService()
    patient_service.repository = Mock()
    return patient_service


# ---------------- ADD PATIENT TESTS ----------------

def test_add_patient_success(service):
    service.repository.add_patient.return_value = True

    result = service.add_patient(
        name="Test Patient",
        age=30,
        gender="Female",
        phone="9876543210",
        address="Hyderabad"
    )

    assert result is True
    service.repository.add_patient.assert_called_once()

    patient = service.repository.add_patient.call_args[0][0]
    assert isinstance(patient, Patient)
    assert patient.name == "Test Patient"
    assert patient.age == 30
    assert patient.phone == "9876543210"


def test_add_patient_missing_name(service):
    with pytest.raises(
        ValueError,
        match="Patient name is required"
    ):
        service.add_patient(
            name="",
            age=30,
            gender="Female",
            phone="9876543210",
            address="Hyderabad"
        )

    service.repository.add_patient.assert_not_called()


def test_add_patient_invalid_age(service):
    with pytest.raises(
        ValueError,
        match="Age must be greater than 0"
    ):
        service.add_patient(
            name="Test Patient",
            age=0,
            gender="Female",
            phone="9876543210",
            address="Hyderabad"
        )

    service.repository.add_patient.assert_not_called()


def test_add_patient_missing_phone(service):
    with pytest.raises(
        ValueError,
        match="Phone number is required"
    ):
        service.add_patient(
            name="Test Patient",
            age=30,
            gender="Female",
            phone="",
            address="Hyderabad"
        )

    service.repository.add_patient.assert_not_called()


def test_add_patient_age_none_is_allowed(service):
    service.repository.add_patient.return_value = True

    result = service.add_patient(
        name="Test Patient",
        age=None,
        gender="Female",
        phone="9876543210",
        address="Hyderabad"
    )

    assert result is True


# ---------------- GET ALL PATIENTS TESTS ----------------

def test_get_all_patients_success(service):
    patients = [
        Patient(
            name="Patient One",
            age=25,
            gender="Female",
            phone="1111111111",
            address="Hyderabad",
            patient_id=1
        ),
        Patient(
            name="Patient Two",
            age=35,
            gender="Male",
            phone="2222222222",
            address="Warangal",
            patient_id=2
        )
    ]

    service.repository.get_all_patients.return_value = patients

    result = service.get_all_patients()

    assert len(result) == 2
    assert result[0].name == "Patient One"
    service.repository.get_all_patients.assert_called_once()


def test_get_all_patients_empty(service):
    service.repository.get_all_patients.return_value = []

    result = service.get_all_patients()

    assert result == []


# ---------------- GET PATIENT BY ID TESTS ----------------

def test_get_patient_by_id_success(service):
    patient = Patient(
        name="Test Patient",
        age=30,
        gender="Female",
        phone="9876543210",
        address="Hyderabad",
        patient_id=101
    )

    service.repository.get_patient_by_id.return_value = patient

    result = service.get_patient_by_id(101)

    assert result.patient_id == 101
    assert result.name == "Test Patient"
    service.repository.get_patient_by_id.assert_called_once_with(101)


@pytest.mark.parametrize("patient_id", [0, -1])
def test_get_patient_by_id_invalid_id(service, patient_id):
    with pytest.raises(
        ValueError,
        match="Patient ID must be greater than 0"
    ):
        service.get_patient_by_id(patient_id)

    service.repository.get_patient_by_id.assert_not_called()


def test_get_patient_by_id_not_found(service):
    service.repository.get_patient_by_id.return_value = None

    result = service.get_patient_by_id(999)

    assert result is None


# ---------------- UPDATE PATIENT TESTS ----------------

def test_update_patient_success(service):
    service.repository.update_patient.return_value = True

    result = service.update_patient(
        patient_id=101,
        name="Updated Patient",
        age=31,
        gender="Female",
        phone="9876543210",
        address="Hyderabad"
    )

    assert result is True
    service.repository.update_patient.assert_called_once()

    patient = service.repository.update_patient.call_args[0][0]
    assert isinstance(patient, Patient)
    assert patient.patient_id == 101
    assert patient.name == "Updated Patient"
    assert patient.age == 31


def test_update_patient_invalid_id(service):
    with pytest.raises(
        ValueError,
        match="Patient ID must be greater than 0"
    ):
        service.update_patient(
            patient_id=0,
            name="Test Patient",
            age=30,
            gender="Female",
            phone="9876543210",
            address="Hyderabad"
        )

    service.repository.update_patient.assert_not_called()


def test_update_patient_missing_name(service):
    with pytest.raises(
        ValueError,
        match="Patient name is required"
    ):
        service.update_patient(
            patient_id=101,
            name="",
            age=30,
            gender="Female",
            phone="9876543210",
            address="Hyderabad"
        )

    service.repository.update_patient.assert_not_called()


def test_update_patient_invalid_age(service):
    with pytest.raises(
        ValueError,
        match="Age must be greater than 0"
    ):
        service.update_patient(
            patient_id=101,
            name="Test Patient",
            age=0,
            gender="Female",
            phone="9876543210",
            address="Hyderabad"
        )

    service.repository.update_patient.assert_not_called()


def test_update_patient_missing_phone(service):
    with pytest.raises(
        ValueError,
        match="Phone number is required"
    ):
        service.update_patient(
            patient_id=101,
            name="Test Patient",
            age=30,
            gender="Female",
            phone="",
            address="Hyderabad"
        )

    service.repository.update_patient.assert_not_called()


# ---------------- DELETE PATIENT TESTS ----------------

def test_delete_patient_success(service):
    service.repository.delete_patient.return_value = True

    result = service.delete_patient(101)

    assert result is True
    service.repository.delete_patient.assert_called_once_with(101)


@pytest.mark.parametrize("patient_id", [0, -1])
def test_delete_patient_invalid_id(service, patient_id):
    with pytest.raises(
        ValueError,
        match="Patient ID must be greater than 0"
    ):
        service.delete_patient(patient_id)

    service.repository.delete_patient.assert_not_called()


def test_delete_patient_not_found(service):
    service.repository.delete_patient.return_value = False

    result = service.delete_patient(999)

    assert result is False