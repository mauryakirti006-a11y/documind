from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pathlib import Path
import shutil
import sys
import faiss


# ============================================================
# PATHS
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# ============================================================
# IMPORTS
# ============================================================

from processor import process_file

from rag.chunking import (
    normalize_document,
    save_chunks
)

from rag.embeddings import (
    create_embeddings
)

from rag.vector_store import (
    create_vector_store
)

from rag.retrieval import (
    retrieve_information
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Document Intelligence API"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# DIRECTORIES
# ============================================================

UPLOAD_DIR = BACKEND_DIR / "uploads"
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

INDEX_PATH = DATA_DIR / "documents.index"

CHUNKS_PATH = DATA_DIR / "chunks.json"


# ============================================================
# QUESTION MODEL
# ============================================================

class QuestionRequest(BaseModel):

    question: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Backend is running",
        "status": "success"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@app.post("/api/files/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )


    # --------------------------------------------------------
    # SUPPORTED FILE TYPES
    # --------------------------------------------------------

    supported_extensions = {

        ".pdf",
        ".docx",
        ".txt",
        ".csv",
        ".xlsx",
        ".pptx",
        ".png",
        ".jpg",
        ".jpeg"

    }


    extension = Path(
        file.filename
    ).suffix.lower()


    if extension not in supported_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {extension}"
            )
        )


    print()
    print("=" * 60)
    print("STARTING DOCUMENT UPLOAD")
    print("=" * 60)

    print(
        "Filename:",
        file.filename
    )


    # ========================================================
    # SAVE FILE
    # ========================================================

    file_path = UPLOAD_DIR / file.filename


    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )


    except Exception as error:

        print(
            "FILE SAVE ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not save file: {error}"
            )
        )


    print(
        "File saved:",
        file_path
    )


    # ========================================================
    # STEP 1 - EXTRACT DOCUMENT
    # ========================================================

    try:

        print()
        print(
            "STEP 1: Extracting document..."
        )


        extracted_data = process_file(
            file_path
        )


        print(
            "Document type:",
            extracted_data.get("type")
        )


        print(
            "Document extracted successfully"
        )


    except Exception as error:

        print(
            "PROCESSOR ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Document extraction failed: {error}"
            )
        )


    # ========================================================
    # STEP 2 - NORMALIZE + CHUNK
    # ========================================================

    try:

        print()
        print(
            "STEP 2: Creating chunks..."
        )


        chunks = normalize_document(
            extracted_data,
            file.filename
        )


        if not chunks:

            raise ValueError(
                "No text was extracted from the document."
            )


        print(
            "Chunks created:",
            len(chunks)
        )


    except Exception as error:

        print(
            "CHUNKING ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Chunking failed: {error}"
            )
        )


    # ========================================================
    # STEP 3 - SAVE CHUNKS
    # ========================================================

    try:

        print()
        print(
            "STEP 3: Saving chunks..."
        )


        save_chunks(
            chunks
        )


        print(
            "Chunks saved:",
            CHUNKS_PATH
        )


    except Exception as error:

        print(
            "CHUNK SAVE ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not save chunks: {error}"
            )
        )


    # ========================================================
    # STEP 4 - CREATE EMBEDDINGS
    # ========================================================

    try:

        print()
        print(
            "STEP 4: Creating embeddings..."
        )


        texts = [

            chunk["text"]

            for chunk in chunks

        ]


        embeddings = create_embeddings(
            texts
        )


        print(
            "Embeddings created:",
            len(embeddings)
        )


        print(
            "Embedding dimension:",
            embeddings.shape[1]
        )


    except Exception as error:

        print(
            "EMBEDDING ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Embedding creation failed: {error}"
            )
        )


    # ========================================================
    # STEP 5 - CREATE FAISS INDEX
    # ========================================================

    try:

        print()
        print(
            "STEP 5: Creating FAISS index..."
        )


        index = create_vector_store(
            embeddings
        )


        print(
            "FAISS vectors:",
            index.ntotal
        )


    except Exception as error:

        print(
            "FAISS ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"FAISS creation failed: {error}"
            )
        )


    # ========================================================
    # STEP 6 - SAVE FAISS INDEX
    # ========================================================

    try:

        print()
        print(
            "STEP 6: Saving FAISS index..."
        )


        faiss.write_index(
            index,
            str(INDEX_PATH)
        )


        print(
            "FAISS index saved:",
            INDEX_PATH
        )


    except Exception as error:

        print(
            "FAISS SAVE ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not save FAISS index: {error}"
            )
        )


    # ========================================================
    # COMPLETE
    # ========================================================

    print()
    print("=" * 60)
    print(
        "RAG PROCESSING COMPLETE"
    )
    print("=" * 60)


    return {

        "success": True,

        "filename": file.filename,

        "chunks_created": len(chunks),

        "vectors_created": index.ntotal,

        "message": (
            "Document uploaded and "
            "RAG index created successfully"
        )

    }


# ============================================================
# ASK QUESTION
# ============================================================

@app.post("/api/ask")
def ask_question(
    request: QuestionRequest
):

    question = request.question.strip()


    # ========================================================
    # EMPTY QUESTION
    # ========================================================

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )


    print()
    print("=" * 60)
    print("RAG QUESTION")
    print("=" * 60)

    print(
        "Question:",
        question
    )


    # ========================================================
    # CASUAL QUESTIONS
    # ========================================================

    casual_questions = [

        "hi",
        "hello",
        "hey",

        "how are you",
        "how are you?",

        "who are you",
        "who are you?",

        "what are you",
        "what are you?",

        "what can you do",
        "what can you do?",

        "good morning",
        "good afternoon",
        "good evening",
        "good night",

        "thanks",
        "thank you",
        "thank you!",

        "bye",
        "goodbye"

    ]


    normalized_question = (

        question
        .lower()
        .strip()
        .replace("!", "")
        .replace(".", "")

    )


    if normalized_question in casual_questions:

        print(
            "Casual question detected."
        )

        print(
            "Skipping document retrieval."
        )


        return {

            "success": True,

            "question": question,

            "answer": (
                "I'm just a document "
                "question-answering assistant. "
                "Ask me something about your "
                "uploaded document."
            ),

            "results": [],

            "result_count": 0,

            "relevant": False,

            "casual": True

        }


    # ========================================================
    # CHECK RAG FILES
    # ========================================================

    if not INDEX_PATH.exists():

        raise HTTPException(

            status_code=404,

            detail=(
                "No document has been uploaded yet."
            )

        )


    if not CHUNKS_PATH.exists():

        raise HTTPException(

            status_code=404,

            detail=(
                "Document chunks are missing. "
                "Please upload the document again."
            )

        )


    # ========================================================
    # RETRIEVE INFORMATION
    # ========================================================

    try:

        result = retrieve_information(

            question,

            top_k=5

        )


    except Exception as error:

        print(
            "RETRIEVAL ERROR:",
            error
        )

        raise HTTPException(

            status_code=500,

            detail=(
                f"RAG retrieval failed: {error}"
            )

        )


    results = result.get(

        "results",

        []

    )


    print(

        "Retrieved chunks:",

        len(results)

    )


    # ========================================================
    # NO RESULTS
    # ========================================================

    if not results:

        return {

            "success": True,

            "question": question,

            "answer": (
                "I could not find relevant "
                "information in the uploaded "
                "document."
            ),

            "results": [],

            "result_count": 0,

            "relevant": False,

            "casual": False

        }


    # ========================================================
    # BUILD OLLAMA CONTEXT
    # ========================================================

    context_parts = []


    for number, item in enumerate(

        results,

        start=1

    ):

        text = item.get(

            "text",

            ""

        ).strip()


        if not text:

            continue


        document = item.get(

            "document",

            "Unknown document"

        )


        page = item.get(

            "page"

        )


        slide = item.get(

            "slide"

        )


        sheet = item.get(

            "sheet"

        )


        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        if page is not None:

            location = (
                f"Page {page}"
            )


        elif slide is not None:

            location = (
                f"Slide {slide}"
            )


        elif sheet:

            location = (
                f"Sheet {sheet}"
            )


        else:

            location = (
                "Location not available"
            )


        context_parts.append(

            f"""
SOURCE {number}

Document:
{document}

Location:
{location}

Content:
{text}
"""

        )


    context = "\n".join(
        context_parts
    )


    # ========================================================
    # SEND TO OLLAMA
    # ========================================================

    try:

        from llm import generate_answer


        print()
        print(
            "Sending retrieved context to Ollama..."
        )


        answer = generate_answer(

            question,

            context

        )


        print(
            "Ollama answer generated successfully"
        )


    except Exception as error:

        print(
            "OLLAMA ERROR:",
            error
        )


        answer = (

            "I found relevant information "
            "in the uploaded document, but I "
            "could not generate the AI answer."

        )


    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return {

        "success": True,

        "question": question,

        "answer": answer,

        "results": results,

        "result_count": len(results),

        "relevant": True,

        "casual": False

    }


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn


    uvicorn.run(

        "main:app",

        host="0.0.0.0",

        port=8000,

        reload=True

    )