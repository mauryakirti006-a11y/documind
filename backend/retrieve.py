import json
import faiss
from sentence_transformers import SentenceTransformer


# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Load FAISS index
index = faiss.read_index("data/documents.index")


# Load document chunks
with open("data/chunks.json", "r", encoding="utf-8") as file:
    chunks = json.load(file)


def retrieve_information(question, top_k=5, threshold=1.8):

    # Convert user question into an embedding
    question_embedding = model.encode([question])

    # Search for the most relevant chunks
    distances, indices = index.search(
        question_embedding,
        top_k
    )

    results = []

    for distance, index_number in zip(distances[0], indices[0]):

        # Ignore invalid results
        if index_number == -1:
            continue

        # Ignore results that are not relevant enough
        if distance > threshold:
            continue

        chunk = chunks[index_number]

        # Keep only the information needed by our application
        result = {
            "text": chunk.get("text"),
            "document": chunk.get("document"),
            "page": chunk.get("page"),
            "slide": chunk.get("slide"),

            # Optional image information
            # Will be None until the document-processing
            # pipeline provides an image path.
            "image_path": chunk.get("image_path"),

            # Internal retrieval distance
            "distance": float(distance)
        }

        results.append(result)

    return results


if __name__ == "__main__":

    question = input("Ask a question: ")

    results = retrieve_information(question)

    print("\nRetrieved Information:\n")

    if not results:

        print("❌ No relevant information found in the uploaded documents.")

    else:

        for result in results:

            print("Content:", result["text"])
            print("Retrieved from:", result["document"])

            if result["page"] is not None:
                print("Page:", result["page"])

            if result["slide"] is not None:
                print("Slide:", result["slide"])

            if result["image_path"] is not None:
                print("Related Image:", result["image_path"])

            print("-" * 50)