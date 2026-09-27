from pathlib import Path
import json
import faiss

from rag.embeddings import create_embeddings


# ============================================================
# PATHS
# ============================================================

RAG_DIR = Path(__file__).resolve().parent
BACKEND_DIR = RAG_DIR.parent
PROJECT_DIR = BACKEND_DIR.parent

INDEX_PATH = PROJECT_DIR / "data" / "documents.index"
CHUNKS_PATH = PROJECT_DIR / "data" / "chunks.json"


# ============================================================
# RETRIEVE INFORMATION
# ============================================================

def retrieve_information(question, top_k=5):

    # --------------------------------------------------------
    # CHECK FILES
    # --------------------------------------------------------

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            f"FAISS index not found: {INDEX_PATH}"
        )

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"Chunks file not found: {CHUNKS_PATH}"
        )


    # --------------------------------------------------------
    # LOAD FAISS INDEX
    # --------------------------------------------------------

    index = faiss.read_index(
        str(INDEX_PATH)
    )


    # --------------------------------------------------------
    # LOAD CHUNKS
    # --------------------------------------------------------

    with open(
        CHUNKS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)


    # --------------------------------------------------------
    # CREATE QUESTION EMBEDDING
    # --------------------------------------------------------

    question_embedding = create_embeddings(
        [question]
    )


    # --------------------------------------------------------
    # SEARCH FAISS
    # --------------------------------------------------------

    actual_top_k = min(
        top_k,
        index.ntotal
    )

    distances, indices = index.search(
        question_embedding,
        actual_top_k
    )


    # --------------------------------------------------------
    # BUILD RESULTS
    # --------------------------------------------------------

    results = []

    for distance, index_number in zip(
        distances[0],
        indices[0]
    ):

        if index_number < 0:
            continue

        if index_number >= len(chunks):
            continue


        chunk = chunks[index_number]


        results.append({

            "text": chunk.get(
                "text",
                ""
            ),

            "document": chunk.get(
                "document",
                "Unknown"
            ),

            "page": chunk.get(
                "page"
            ),

            "slide": chunk.get(
                "slide"
            ),

            "sheet": chunk.get(
                "sheet"
            ),

            "section": chunk.get(
                "section"
            ),

            "visual": chunk.get(
                "visual"
            ),

            "distance": float(
                distance
            )

        })


    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {

        "results": results,

        "count": len(results)

    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    question = input(
        "Ask a question: "
    )

    result = retrieve_information(
        question,
        top_k=5
    )

    print()

    print(
        "Retrieved chunks:",
        len(result["results"])
    )

    for number, item in enumerate(
        result["results"],
        start=1
    ):

        print()

        print(
            f"--- Result {number} ---"
        )

        print(
            "Document:",
            item["document"]
        )

        print(
            "Page:",
            item["page"]
        )

        print(
            "Sheet:",
            item["sheet"]
        )

        print(
            "Distance:",
            item["distance"]
        )

        print(
            "Text:",
            item["text"][:500]
        )