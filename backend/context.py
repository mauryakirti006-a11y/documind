def build_context(retrieved_chunks):
    """
    Converts retrieved document chunks into a clean
    context that can be given to the AI model.
    """

    context = ""

    for chunk in retrieved_chunks:

        context += (
            f"Source: {chunk['file']}\n"
            f"Page: {chunk['page']}\n"
            f"Content: {chunk['text']}\n\n"
        )

    return context


if __name__ == "__main__":

    # Temporary sample data
    # Later this will come from retrieve.py

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

    context = build_context(sample_chunks)

    print("Context for AI:")
    print(context)