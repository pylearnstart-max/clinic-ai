from pathlib import Path


def load_document(file_path: str) -> str:
    """Read a UTF-8 text document."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    return path.read_text(encoding="utf-8-sig")


def split_into_chunks(text: str) -> list[str]:
    """Split a document into smaller paragraph-based chunks."""
    chunks = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    return chunks


if __name__ == "__main__":
    document_path = (
        Path(__file__).resolve().parent.parent
        / "knowledge_base"
        / "clinic_faq.txt"
    )

    document = load_document(str(document_path))
    chunks = split_into_chunks(document)

    print(f"Total chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):
        print(f"\nChunk {index}:")
        print(chunk)
