def extract_evidence(retrieved_chunks):
    """
    Extracts source information from the retrieved chunks.
    """

    evidence = []

    for chunk in retrieved_chunks:

        source = {
            "file": chunk["file"],
            "page": chunk["page"],
            "text": chunk["text"]
        }

        evidence.append(source)

    return evidence


if __name__ == "__main__":

    # Temporary sample data
    sample_chunks = [
        {
            "text": "The total project budget for 2025 was ₹10 lakh.",
            "file": "project_report.pdf",
            "page": 12
        },
        {
            "text": "The project was completed in December 2025.",
            "file": "project_report.pdf",
            "page": 24
        }
    ]

    evidence = extract_evidence(sample_chunks)

    print("Evidence:")

    for item in evidence:
        print(f"File: {item['file']}")
        print(f"Page: {item['page']}")
        print(f"Text: {item['text']}")
        print()