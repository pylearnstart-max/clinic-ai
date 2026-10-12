
from fastembed import TextEmbedding

from app.ai.retriever import (
    MODEL_NAME,
    load_clinic_chunks,
    retrieve_relevant_chunks,
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
    assert any("Monday to Saturday" in chunk for chunk in results)


def test_empty_question_returns_empty_list():
    model = TextEmbedding(model_name=MODEL_NAME)
    chunks = load_clinic_chunks()

    assert retrieve_relevant_chunks("", chunks, model) == []


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