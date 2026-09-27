from sentence_transformers import SentenceTransformer
import numpy as np


# ============================================================
# EMBEDDING MODEL
# ============================================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# CREATE EMBEDDINGS
# ============================================================

def create_embeddings(texts):

    embeddings = model.encode(
        texts,
        convert_to_numpy=True
    )

    return np.asarray(
        embeddings,
        dtype="float32"
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    texts = [
        "What is FinTech?",
        "Financial technology improves financial services."
    ]

    embeddings = create_embeddings(texts)

    print(
        "Number of texts:",
        len(texts)
    )

    print(
        "Embedding shape:",
        embeddings.shape
    )