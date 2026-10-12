from app.ai.document_loader import split_into_chunks


def test_split_into_chunks():
    text = "Clinic Timings:\n9 AM to 6 PM.\n\nAppointment Policy:\nBook before visiting.\n\n"

    chunks = split_into_chunks(text)

    assert len(chunks) == 2
    assert "Clinic Timings" in chunks[0]
    assert "Appointment Policy" in chunks[1]

    print("PASS: Document chunking works correctly.")


if __name__ == "__main__":
    test_split_into_chunks()
