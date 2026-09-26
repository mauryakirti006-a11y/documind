def retrieve_information(question):
    """
    Temporary retrieval function.

    Later, this will be connected to Member 2's
    vector database / retrieval system.
    """

    retrieved_chunks = [
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

    return retrieved_chunks


if __name__ == "__main__":

    question = "What was the project budget?"

    results = retrieve_information(question)

    print("Retrieved Information:")
    print(results)