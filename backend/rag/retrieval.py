import json
import os

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

DATA_DIR = os.path.join(BASE_DIR, "data")

INDEX_PATH = os.path.join(
    DATA_DIR,
    "documents.index"
)

CHUNKS_PATH = os.path.join(
    DATA_DIR,
    "chunks.json"
)


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------------------------
# LOAD FAISS INDEX
# --------------------------------------------------

if not os.path.exists(INDEX_PATH):
    raise FileNotFoundError(
        f"FAISS index not found: {INDEX_PATH}"
    )

index = faiss.read_index(INDEX_PATH)


# --------------------------------------------------
# LOAD CHUNKS
# --------------------------------------------------

if not os.path.exists(CHUNKS_PATH):
    raise FileNotFoundError(
        f"chunks.json not found: {CHUNKS_PATH}"
    )

with open(
    CHUNKS_PATH,
    "r",
    encoding="utf-8"
) as file:

    chunks = json.load(file)


# --------------------------------------------------
# SAFETY CHECK
# --------------------------------------------------

if index.ntotal != len(chunks):

    raise ValueError(
        f"FAISS/chunks mismatch: "
        f"{index.ntotal} vectors but "
        f"{len(chunks)} chunks."
    )


# --------------------------------------------------
# RETRIEVAL FUNCTION
# --------------------------------------------------

def retrieve_information(
    question,
    top_k=5,
    threshold=1.5
):
    """
    Search the FAISS vector database for chunks
    relevant to the user's question.

    Returns:
        {
            "relevant": True/False,
            "results": [...]
        }
    """

    # Check empty question
    if not question or not question.strip():

        return {
            "relevant": False,
            "results": []
        }

    question = question.strip()

    # --------------------------------------------------
    # CREATE QUESTION EMBEDDING
    # --------------------------------------------------

    question_embedding = model.encode(
        [question],
        convert_to_numpy=True
    )

    question_embedding = np.asarray(
        question_embedding,
        dtype="float32"
    )

    # --------------------------------------------------
    # SEARCH FAISS
    # --------------------------------------------------

    search_k = min(
        top_k,
        index.ntotal
    )

    distances, indices = index.search(
        question_embedding,
        search_k
    )

    results = []

    # --------------------------------------------------
    # PROCESS RESULTS
    # --------------------------------------------------

    for distance, index_number in zip(
        distances[0],
        indices[0]
    ):

        # Invalid FAISS result
        if index_number == -1:
            continue

        # Ignore results that are too far away
        if float(distance) > threshold:
            continue

        # Safety check
        if index_number >= len(chunks):
            continue

        chunk = chunks[index_number]

        results.append({
            "text": chunk.get("text", ""),
            "document": chunk.get("document"),
            "page": chunk.get("page"),
            "slide": chunk.get("slide"),
            "sheet": chunk.get("sheet"),
            "section": chunk.get("section"),
            "distance": float(distance)
        })

    # --------------------------------------------------
    # RELEVANCE DECISION
    # --------------------------------------------------

    if len(results) == 0:

        return {
            "relevant": False,
            "results": []
        }

    return {
        "relevant": True,
        "results": results
    }


# --------------------------------------------------
# COMMAND-LINE TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("DOCUMENT RETRIEVAL TEST")
    print("=" * 60)

    print(
        f"Loaded vectors: {index.ntotal}"
    )

    print(
        f"Loaded chunks: {len(chunks)}"
    )

    print()

    question = input(
        "Ask a question: "
    ).strip()

    output = retrieve_information(
        question
    )

    print()
    print("=" * 60)

    if not output["relevant"]:

        print(
            "❌ IRRELEVANT QUESTION"
        )

        print(
            "This question is not related "
            "to the uploaded document."
        )

    else:

        print(
            "✅ RELEVANT QUESTION"
        )

        print(
            f"Retrieved chunks: "
            f"{len(output['results'])}"
        )

        print("=" * 60)

        for number, result in enumerate(
            output["results"],
            start=1
        ):

            print()
            print(
                f"--- Result {number} ---"
            )

            print(
                "Document:",
                result["document"]
            )

            print(
                "Page:",
                result["page"]
            )

            print(
                "Slide:",
                result["slide"]
            )

            print(
                "Sheet:",
                result["sheet"]
            )

            print(
                "Section:",
                result["section"]
            )

            print(
                "Distance:",
                result["distance"]
            )

            print(
                "Content:",
                result["text"]
            )