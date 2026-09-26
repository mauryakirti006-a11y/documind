import json
import os


def create_chunks(text, chunk_size=100, overlap=20):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start = end - overlap

    return chunks


def save_chunks(chunks, document_name, page=1, section="Unknown"):
    data = []

    for i, chunk in enumerate(chunks):
        data.append({
            "id": i,
            "text": chunk,
            "document": document_name,
            "page": page,
            "section": section
        })

    os.makedirs("../data", exist_ok=True)

    with open("../data/chunks.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":

    text = """
    Artificial intelligence is used to analyze documents.
    Document intelligence helps organizations search large collections.
    OCR can extract text from scanned documents.
    Semantic search helps users find information based on meaning.
    """

    chunks = create_chunks(text)

    save_chunks(
        chunks,
        "sample_document.pdf",
        page=1,
        section="Introduction"
    )

    print("Chunks saved successfully!")