def generate_answer(question, context):
    """
    Generates an answer using the retrieved context.

    This is a temporary version.
    Later, we will connect this function to an actual LLM.
    """

    # Temporary answer for testing
    answer = (
        "Based on the provided document, "
        "the total project budget for 2025 was ₹10 lakh."
    )

    return answer


if __name__ == "__main__":

    question = "What was the project budget?"

    context = """
    Source: project_report.pdf
    Page: 12
    Content: The total project budget for 2025 was ₹10 lakh.
    """

    answer = generate_answer(question, context)

    print("AI Answer:")
    print(answer)