# ============================================================
# CREATE CONTEXT FOR LLM
# ============================================================

def create_context(retrieved_information):

    context = ""

    # Handle dictionary returned by retrieval.py
    if isinstance(retrieved_information, dict):

        retrieved_information = retrieved_information.get(
            "results",
            []
        )

    # Handle empty results
    if not retrieved_information:

        return ""

    # Build context
    for number, item in enumerate(
        retrieved_information,
        start=1
    ):

        context += f"""

========================
SOURCE {number}
========================

Document: {item.get("document", "Unknown")}
Page: {item.get("page", "N/A")}
Slide: {item.get("slide", "N/A")}
Sheet: {item.get("sheet", "N/A")}
Section: {item.get("section", "N/A")}

Content:
{item.get("text", "")}

"""

    return context.strip()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from retrieve import retrieve

    question = input("Ask a question: ")

    results = retrieve(
        question,
        top_k=5
    )

    context = create_context(
        results
    )

    print("\nContext for AI:\n")
    print(context)