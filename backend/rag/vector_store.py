import faiss
import numpy as np
import os

from embeddings import create_embeddings


def create_vector_store(embeddings):
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index


if __name__ == "__main__":

    texts = [
        "Artificial intelligence is used to analyze documents.",
        "Document intelligence helps organizations search large collections.",
        "OCR can extract text from scanned documents.",
        "Semantic search helps users find information based on meaning."
    ]

    embeddings = create_embeddings(texts)

    index = create_vector_store(embeddings)

    os.makedirs("../data", exist_ok=True)

    faiss.write_index(index, "../data/documents.index")

    print("Vector database saved successfully!")
    print("Number of vectors:", index.ntotal)