from retrieve import retrieve_information


def create_context(retrieved_information):
    context = ""

    for item in retrieved_information:
        context += f"""
Source: {item['document']}
Page: {item['page']}
Slide: {item['slide']}
Content: {item['text']}
"""

    return context


if __name__ == "__main__":

    question = input("Ask a question: ")

    results = retrieve_information(question)

    context = create_context(results)

    print("\nContext for AI:\n")
    print(context)