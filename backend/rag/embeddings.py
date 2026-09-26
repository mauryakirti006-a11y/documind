from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(texts):
    return model.encode(texts)


if __name__ == "__main__":
    texts = [
        "Employees get 18 days of annual leave.",
        "The company provides health insurance.",
        "Employees must submit leave requests."
    ]

    embeddings = create_embeddings(texts)

    print("Number of texts:", len(texts))
    print("Embedding shape:", embeddings.shape)