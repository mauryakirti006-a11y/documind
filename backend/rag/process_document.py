from pathlib import Path

from backend.processor import process_file
from rag.chunking import normalize_document, save_chunks


def process_document(file_path):

    file_path = Path(file_path)

    print("Processing file:", file_path.name)

    # -----------------------------
    # MEMBER 2
    # Extract text/data
    # -----------------------------

    extracted_data = process_file(file_path)

    print("Document type:", extracted_data.get("type"))

    # -----------------------------
    # MEMBER 3A
    # Convert extracted data
    # into RAG chunks
    # -----------------------------

    chunks = normalize_document(
        extracted_data,
        file_path.name
    )

    print("Number of chunks:", len(chunks))

    # Save chunks.json
    save_chunks(chunks)

    return chunks


if __name__ == "__main__":

    # Change this to your test file
    test_file = Path(
        "../../Hackstreak ppt 2.pptx"
    )

    chunks = process_document(test_file)

    print("\nProcessing completed!")
    print("Chunks created:", len(chunks))