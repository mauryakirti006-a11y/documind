def generate_answer(question, retrieved_information):

    if not retrieved_information:
        return {
            "answer": "I could not find relevant information in the uploaded documents.",
            "sources": []
        }

    best_result = retrieved_information[0]

    answer = best_result["text"]

    sources = []

    for item in retrieved_information:
        sources.append({
            "document": item["document"],
            "page": item["page"],
            "slide": item["slide"],
            "section": item["section"]
        })

    return {
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":

    sample_results = [
        {
            "text": "A self-forming offline communication network.",
            "document": "Hackstreak ppt 2.pptx",
            "page": None,
            "slide": 2,
            "section": "Unknown"
        }
    ]

    result = generate_answer(
        "What is the proposed solution?",
        sample_results
    )

    print("\nAnswer:")
    print(result["answer"])

    print("\nSources:")

    for source in result["sources"]:
        print(source["document"])
        print("Page:", source["page"])
        print("Slide:", source["slide"])