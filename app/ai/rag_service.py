
from fastembed import TextEmbedding

from app.ai.retriever import (
    MODEL_NAME,
    load_clinic_chunks,
    retrieve_scored_chunks,
)


class ClinicRAGService:
    """Generate answers using retrieved demo clinic FAQ information."""

    def __init__(self):
        self.model = TextEmbedding(model_name=MODEL_NAME)
        self.chunks = load_clinic_chunks()

    def answer_question(self, question: str) -> str:
        """Answer a question using relevant FAQ chunks."""

        if not question or not question.strip():
            return "Please enter a question."

        results = retrieve_scored_chunks(
            question=question,
            chunks=self.chunks,
            model=self.model,
            top_k=1,
        )

        if not results:
            return (
                "I could not find this information in the "
                "demo clinic FAQ. Please contact clinic reception."
            )

        context = "\n\n".join(
            chunk for chunk, score in results
        )

        return (
            "Based on the demo clinic FAQ:\n\n"
            f"{context}"
        )


if __name__ == "__main__":
    rag_service = ClinicRAGService()

    questions = [
        "What are the clinic timings?",
        "How can I confirm doctor availability?",
        "What should I do in a medical emergency?",
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        print("Answer:")
        print(rag_service.answer_question(question))
        print("-" * 50)