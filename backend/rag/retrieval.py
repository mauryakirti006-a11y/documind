import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# PATHS
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_DIR / "data"

INDEX_PATH = DATA_DIR / "documents.index"
CHUNKS_PATH = DATA_DIR / "chunks.json"


# --------------------------------------------------
# EMBEDDING MODEL
# --------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------------------------
# RETRIEVE INFORMATION
# --------------------------------------------------

def retrieve_information(question, top_k=5):

    # --------------------------------------------------
    # CHECK FILES
    # --------------------------------------------------

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            f"FAISS index not found: {INDEX_PATH}"
        )

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"chunks.json not found: {CHUNKS_PATH}"
        )


    # --------------------------------------------------
    # LOAD FAISS INDEX
    # --------------------------------------------------

    index = faiss.read_index(
        str(INDEX_PATH)
    )


    # --------------------------------------------------
    # LOAD CHUNKS
    # --------------------------------------------------

    with open(
        CHUNKS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)


    # --------------------------------------------------
    # CHECK INDEX / CHUNK COUNT
    # --------------------------------------------------

    if index.ntotal == 0:

        return []


    if len(chunks) == 0:

        return []


    # --------------------------------------------------
    # CREATE QUESTION EMBEDDING
    # --------------------------------------------------

    question_embedding = model.encode(
        [question],
        convert_to_numpy=True
    ).astype("float32")


    # --------------------------------------------------
    # SEARCH FAISS
    # --------------------------------------------------

    number_to_search = min(
        top_k,
        index.ntotal,
        len(chunks)
    )


    distances, indices = index.search(
        question_embedding,
        number_to_search
    )


    # --------------------------------------------------
    # CREATE RESULTS
    # --------------------------------------------------

    results = []


    for distance, index_number in zip(
        distances[0],
        indices[0]
    ):

        # Invalid FAISS result
        if index_number == -1:
            continue


        # Prevent IndexError
        if index_number >= len(chunks):
            continue


        chunk = chunks[index_number]


        results.append({

            "text": chunk.get(
                "text",
                ""
            ),

            "document": chunk.get(
                "document"
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

            "distance": float(
                distance
            )

        })


    return results


# --------------------------------------------------
# DIRECT TERMINAL TEST
# --------------------------------------------------

if __name__ == "__main__":

    print(
        "\nDocument Retrieval Test"
    )

    print(
        "Type 'exit' to stop.\n"
    )


    while True:

        question = input(
            "Ask a question: "
        ).strip()


        if question.lower() == "exit":

            break


        if not question:

            print(
                "Please enter a question.\n"
            )

            continue


        try:

            results = retrieve_information(
                question,
                top_k=5
            )


            print(
                "\nRetrieved Information:\n"
            )


            if not results:

                print(
                    "No information found."
                )


            else:

                for number, result in enumerate(
                    results,
                    start=1
                ):

                    print(
                        f"Result {number}"
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

                    print(
                        "-" * 60
                    )


        except Exception as error:

            print(
                "Error:",
                error
            )