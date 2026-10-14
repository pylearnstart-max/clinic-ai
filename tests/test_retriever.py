
from unittest.mock import MagicMock, patch

from fastembed import TextEmbedding

from app.ai.retriever import (
    MODEL_NAME,
    load_clinic_chunks,
    retrieve_relevant_chunks,
    retrieve_scored_chunks,
)


def test_retrieve_clinic_timings():
    model = TextEmbedding(model_name=MODEL_NAME)
    chunks = load_clinic_chunks()

    results = retrieve_relevant_chunks(
        "What are the clinic timings?",
        chunks,
        model,
    )

    assert results
    assert any(
        "Monday to Saturday" in chunk
        for chunk in results
    )


def test_empty_question_returns_empty_list():
    model = TextEmbedding(model_name=MODEL_NAME)
    chunks = load_clinic_chunks()

    assert retrieve_relevant_chunks(
        "",
        chunks,
        model,
    ) == []


def test_zero_top_k_returns_empty_list():
    model = TextEmbedding(model_name=MODEL_NAME)
    chunks = load_clinic_chunks()

    assert retrieve_relevant_chunks(
        "clinic timings",
        chunks,
        model,
        top_k=0,
    ) == []


def test_empty_chunks_returns_empty_list():
    model = TextEmbedding(model_name=MODEL_NAME)

    assert retrieve_relevant_chunks(
        "clinic timings",
        [],
        model,
    ) == []


@patch("app.ai.retriever.np.argsort")
def test_similarity_threshold_filters_low_scores(mock_argsort):
    model = MagicMock()

    # Mock question embedding and two FAQ chunk embeddings.
    model.embed.side_effect = [
        [[1.0, 0.0]],       # Question vector
        [[0.8, 0.6], [0.0, 1.0]],  # FAQ chunk vectors
    ]

    chunks = [
        "Clinic timings information",
        "Unrelated information",
    ]

    # Rank the first chunk before the second.
    mock_argsort.return_value = [1, 0]

    results = retrieve_scored_chunks(
        question="clinic timings",
        chunks=chunks,
        model=model,
        top_k=2,
    )

    # Only the relevant chunk should be returned.
    assert len(results) == 1
    assert results[0][0] == "Clinic timings information"
    assert results[0][1] >= 0.50
  

