import faiss
import numpy as np
import os
import json

from embeddings import create_embeddings


def create_vector_store(embeddings):
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index


if __name__ == "__main__":

    # Path to chunks.json
    chunks_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "data",
        "chunks.json"
    )

    chunks_path = os.path.abspath(chunks_path)

    # Load chunks
    with open(chunks_path, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    # Get exactly the same text that is stored in chunks.json
    texts = [chunk["text"] for chunk in chunks]

    print("Number of chunks:", len(texts))

    # Create embeddings
    embeddings = create_embeddings(texts)

    # Create FAISS index
    index = create_vector_store(embeddings)

    # Save index in the same data folder
    data_folder = os.path.dirname(chunks_path)

    index_path = os.path.join(
        data_folder,
        "documents.index"
    )

    faiss.write_index(index, index_path)

    print("Vector database saved successfully!")
    print("Number of vectors:", index.ntotal)