import re

from backend.rag.retrieval import retrieve_information


# --------------------------------------------------
# CLEAN TEXT
# --------------------------------------------------

def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"\s+", " ", str(text))
    return text.strip()


# --------------------------------------------------
# SPLIT INTO SENTENCES
# --------------------------------------------------

def split_sentences(text):

    text = clean_text(text)

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# --------------------------------------------------
# KEYWORDS
# --------------------------------------------------

def get_keywords(question):

    question = question.lower()

    words = re.findall(
        r"\b[a-zA-Z]{3,}\b",
        question
    )

    stop_words = {
        "what",
        "which",
        "where",
        "when",
        "who",
        "whom",
        "does",
        "this",
        "that",
        "with",
        "from",
        "about",
        "into",
        "have",
        "has",
        "are",
        "the",
        "and",
        "for",
        "how",
        "why",
        "can",
        "could",
        "would",
        "should",
        "please",
        "tell",
        "give",
        "used"
    }

    return [
        word
        for word in words
        if word not in stop_words
    ]


# --------------------------------------------------
# FIND BEST SENTENCES
# --------------------------------------------------

def select_best_sentences(
    question,
    results,
    max_sentences=3
):

    keywords = get_keywords(question)

    candidates = []

    for result in results:

        text = clean_text(
            result.get("text", "")
        )

        sentences = split_sentences(text)

        for sentence in sentences:

            sentence_lower = sentence.lower()

            score = 0

            for keyword in keywords:

                if keyword in sentence_lower:
                    score += 1

            candidates.append(
                (score, sentence)
            )

    if not candidates:
        return []

    candidates.sort(
        key=lambda item: item[0],
        reverse=True
    )

    selected = []

    for score, sentence in candidates:

        if sentence not in selected:

            selected.append(sentence)

        if len(selected) >= max_sentences:
            break

    return selected


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

def summarize_results(
    results,
    max_sentences=4
):

    all_sentences = []

    for result in results:

        text = clean_text(
            result.get("text", "")
        )

        sentences = split_sentences(text)

        for sentence in sentences:

            if sentence not in all_sentences:

                all_sentences.append(sentence)

    if not all_sentences:

        return "No information available to summarize."

    return " ".join(
        all_sentences[:max_sentences]
    )


# --------------------------------------------------
# QUESTION ANSWER
# --------------------------------------------------

def generate_answer(
    question,
    results
):

    if not results:

        return (
            "I could not find relevant information "
            "in the uploaded documents."
        )

    best_sentences = select_best_sentences(
        question,
        results,
        max_sentences=3
    )

    if not best_sentences:

        return (
            "Relevant information was found, "
            "but an answer could not be extracted."
        )

    return " ".join(
        best_sentences
    )


# --------------------------------------------------
# DETECT SUMMARY REQUEST
# --------------------------------------------------

def is_summary_request(question):

    question = question.lower()

    summary_words = [
        "summarize",
        "summarise",
        "summary",
        "briefly explain",
        "give me a summary",
        "short summary",
        "in short",
        "key points",
        "main points"
    ]

    return any(
        phrase in question
        for phrase in summary_words
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def answer_question(question):

    retrieved = retrieve_information(
        question,
        threshold = 2.5
    )

    if not retrieved["relevant"]:

        return {
            "answer": (
                "I could not find relevant information "
                "in the uploaded documents."
            ),
            "sources": []
        }

    results = retrieved["results"]

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    if is_summary_request(question):

        answer = summarize_results(
            results
        )

    # --------------------------------------------------
    # NORMAL QUESTION
    # --------------------------------------------------

    else:

        answer = generate_answer(
            question,
            results
        )


    # --------------------------------------------------
    # SOURCE INFORMATION
    # --------------------------------------------------

    sources = []

    seen = set()

    for result in results:

        source_key = (
            result.get("document"),
            result.get("page"),
            result.get("slide")
        )

        if source_key in seen:
            continue

        seen.add(source_key)

        sources.append({

            "document": result.get(
                "document"
            ),

            "page": result.get(
                "page"
            ),

            "slide": result.get(
                "slide"
            ),

            "visual": result.get(
                "visual"
            )
        })


    return {
        "answer": answer,
        "sources": sources
    }


# --------------------------------------------------
# COMMAND LINE TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("DOCUMENT AI ANSWER SYSTEM")
    print("=" * 60)

    question = input(
        "Ask a question: "
    ).strip()

    output = answer_question(
        question
    )

    print()
    print("ANSWER:")
    print(output["answer"])

    print()
    print("=" * 60)
    print("SOURCE")
    print("=" * 60)

    if not output["sources"]:

        print(
            "No relevant source found."
        )

    else:

        for source in output["sources"]:

            print(
                "Retrieved from:",
                source["document"]
            )

            if source["page"] is not None:

                print(
                    "Page:",
                    source["page"]
                )

            if source["slide"] is not None:

                print(
                    "Slide:",
                    source["slide"]
                )

            if source["visual"]:

                print(
                    "Related visual:",
                    source["visual"]
                )

            print("-" * 40)