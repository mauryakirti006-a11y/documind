import requests


# ============================================================
# OLLAMA SETTINGS
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "llama3.2:3b"


# ============================================================
# GENERATE AI ANSWER
# ============================================================

def generate_answer(question, context):

    prompt = f"""
You are a document question-answering assistant.

You must answer the user's question using the uploaded
document context provided below.

IMPORTANT RULES:

1. Use the document context as the main source.
2. Answer the question directly and clearly.
3. Do NOT require the exact question to appear in the document.
4. If the document contains information that explains the topic,
   use that information to answer.
5. Do NOT say "the question is not relevant" just because the
   exact wording is not present.
6. If the document truly contains no useful information about
   the question, say that the information was not found.
7. Do not invent facts that are not supported by the context.
8. Keep the answer easy to understand.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data.get(
        "response",
        ""
    ).strip()