import faiss
import numpy as np


# ============================================================
# CREATE FAISS VECTOR STORE
# ============================================================

def create_vector_store(embeddings):

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    if len(embeddings) == 0:
        raise ValueError(
            "No embeddings were provided."
        )

    # --------------------------------------------------------
    # Normalize vectors
    # This allows cosine similarity using inner product
    # --------------------------------------------------------

    faiss.normalize_L2(
        embeddings
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embeddings
    )

    return index