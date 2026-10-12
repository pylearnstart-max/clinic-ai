
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

from app.ai.document_loader import load_document, split_into_chunks


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def load_clinic_chunks() -> list[str]:
    """Load the demo clinic FAQ and split it into chunks."""

    document_path = (
        Path(__file__).resolve().parent.parent
        / "knowledge_base"
        / "clinic_faq.txt"
    )

    document = load_document(str(document_path))
    return split_into_chunks(document)


def retrieve_scored_chunks(
    question: str,
    chunks: list[str],
    model: TextEmbedding,
    top_k: int = 2,
) -> list[tuple[str, float]]:
    """Return relevant chunks with their cosine similarity scores."""

    if not question or not question.strip():
        return []

    if not chunks or top_k <= 0:
        return []

    question_vector = np.asarray(
        list(model.embed([question]))[0],
        dtype=np.float32,
    )

    chunk_vectors = np.asarray(
        list(model.embed(chunks)),
        dtype=np.float32,
    )

    question_norm = np.linalg.norm(question_vector)
    chunk_norms = np.linalg.norm(chunk_vectors, axis=1)

    if question_norm == 0:
        return []

    similarities = np.zeros(len(chunks), dtype=np.float32)
    valid = chunk_norms > 0

    similarities[valid] = (
        chunk_vectors[valid] @ question_vector
    ) / (chunk_norms[valid] * question_norm)

    ranked_indices = np.argsort(similarities)[::-1]

    return [
        (chunks[index], float(similarities[index]))
        for index in ranked_indices[:top_k]
        if similarities[index] >= 0.50
    ]


def retrieve_relevant_chunks(
    question: str,
    chunks: list[str],
    model: TextEmbedding,
    top_k: int = 2,
) -> list[str]:
    """Return relevant chunks without their similarity scores."""

    scored_results = retrieve_scored_chunks(
        question,
        chunks,
        model,
        top_k,
    )

    return [chunk for chunk, score in scored_results]


if __name__ == "__main__":
    print("Loading embedding model...")
    embedding_model = TextEmbedding(model_name=MODEL_NAME)

    chunks = load_clinic_chunks()
    question = "What are the clinic timings?"

    results = retrieve_scored_chunks(
        question,
        chunks,
        embedding_model,
        top_k=3,
    )

    print(f"\nQuestion: {question}")
    print("\nSemantic search results:")

    if not results:
        print("No relevant information found.")
    else:
        for index, (chunk, score) in enumerate(results, start=1):
            print(f"\nResult {index} | Similarity: {score:.4f}")
            print(chunk)