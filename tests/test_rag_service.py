
from unittest.mock import MagicMock, patch

from app.ai.rag_service import ClinicRAGService


def make_rag_service():
    service = ClinicRAGService.__new__(ClinicRAGService)
    service.model = MagicMock()
    service.chunks = [
        (
            "Clinic Timings:\n"
            "The demo clinic is open Monday to Saturday, "
            "from 9 AM to 6 PM."
        ),
        (
            "Doctor Information:\n"
            "Doctor schedules may change. Users should contact "
            "clinic reception to confirm doctor availability."
        ),
        (
            "Emergency Policy:\n"
            "For a medical emergency, contact local emergency "
            "services or visit the nearest emergency department."
        ),
    ]
    return service


def test_empty_question_returns_prompt():
    service = make_rag_service()

    assert service.answer_question("") == "Please enter a question."
    assert service.answer_question("   ") == "Please enter a question."


@patch("app.ai.rag_service.retrieve_scored_chunks")
def test_clinic_timings_answer(mock_retrieve):
    service = make_rag_service()
    mock_retrieve.return_value = [(service.chunks[0], 0.75)]

    answer = service.answer_question("What are the clinic timings?")

    assert "Clinic Timings:" in answer
    assert "9 AM to 6 PM" in answer
    assert "Doctor Information:" not in answer


@patch("app.ai.rag_service.retrieve_scored_chunks")
def test_doctor_availability_answer(mock_retrieve):
    service = make_rag_service()
    mock_retrieve.return_value = [(service.chunks[1], 0.68)]

    answer = service.answer_question(
        "How can I confirm doctor availability?"
    )

    assert "Doctor Information:" in answer
    assert "clinic reception" in answer


@patch("app.ai.rag_service.retrieve_scored_chunks")
def test_emergency_answer(mock_retrieve):
    service = make_rag_service()
    mock_retrieve.return_value = [(service.chunks[2], 0.53)]

    answer = service.answer_question(
        "What should I do in a medical emergency?"
    )

    assert "Emergency Policy:" in answer
    assert "local emergency services" in answer
    assert "diagnose conditions or prescribe medication" not in answer


@patch("app.ai.rag_service.retrieve_scored_chunks")
def test_no_relevant_information_returns_fallback(mock_retrieve):
    service = make_rag_service()
    mock_retrieve.return_value = []

    answer = service.answer_question("What is the clinic address?")

    assert "could not find this information" in answer
    assert "contact clinic reception" in answer