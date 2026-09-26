import json
import os


def create_chunks(text, chunk_size=500, overlap=50):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start = end - overlap

    return chunks


def process_slides(extracted_data, document_name):
    all_chunks = []
    chunk_id = 0

    for slide_data in extracted_data["slides"]:

        slide_number = slide_data["slide"]

        # Combine all text from the slide
        slide_text = " ".join(slide_data["text"])

        chunks = create_chunks(slide_text)

        for chunk in chunks:

            all_chunks.append({
                "id": chunk_id,
                "text": chunk,
                "document": document_name,
                "page": None,
                "slide": slide_number,
                "section": "Unknown"
            })

            chunk_id += 1

    return all_chunks


def save_chunks(chunks):

    os.makedirs("../data", exist_ok=True)

    with open(
        "../data/chunks.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            indent=4,
            ensure_ascii=False
        )


if __name__ == "__main__":

    # Test data in Member 2's format
    extracted_data = {
        "type": "pptx",
        "slides": [
            {
                "slide": 1,
                "text": [
                    "HACKSTREAK 3.0 - 2026",
                    "Teams Name: CONNECT4"
                ]
            },
            {
                "slide": 2,
                "text": [
                    "Problem Understanding",
                    "During disasters or network outages, cellular networks may become unavailable.",
                    "Proposed Solution",
                    "A self-forming offline communication network."
                ]
            }
        ]
    }

    chunks = process_slides(
        extracted_data,
        "Hackstreak ppt 2.pptx"
    )

    save_chunks(chunks)

    print("Chunks created successfully!")
    print("Number of chunks:", len(chunks))