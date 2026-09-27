from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from rag.retrieval import retrieve_information


def retrieve(question, top_k=5):

    return retrieve_information(
        question,
        top_k=top_k
    )


if __name__ == "__main__":

    question = input("Ask a question: ")

    result = retrieve(
        question,
        top_k=5
    )

    print("\nRetrieved Information:\n")
    print(result)