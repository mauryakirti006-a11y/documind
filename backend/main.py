from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
from pydantic import BaseModel
import shutil
import uuid
import sys

# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# --------------------------------------------------
# MEMBER 2 - DOCUMENT PROCESSING
# --------------------------------------------------

from processor import process_file


# --------------------------------------------------
# 3A - CHUNKING
# --------------------------------------------------

from rag.chunking import (
    normalize_document,
    save_chunks
)


# --------------------------------------------------
# 3A - EMBEDDINGS + FAISS
# --------------------------------------------------

from rag.embeddings import create_embeddings
from rag.vector_store import create_vector_store


# --------------------------------------------------
# 3B - RETRIEVAL
# --------------------------------------------------

from rag.retrieval import retrieve_information


# --------------------------------------------------
# FAISS
# --------------------------------------------------

import faiss


# --------------------------------------------------
# FASTAPI
# --------------------------------------------------

app = FastAPI(
    title="Document Intelligence API"
)


# --------------------------------------------------
# FOLDERS
# --------------------------------------------------

UPLOAD_DIR = BACKEND_DIR / "uploads"

UPLOAD_DIR.mkdir(
    exist_ok=True
)

DATA_DIR = PROJECT_DIR / "data"

DATA_DIR.mkdir(
    exist_ok=True
)


# --------------------------------------------------
# QUESTION MODEL
# --------------------------------------------------

class QuestionRequest(BaseModel):

    question: str


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Document Intelligence API is running"
    }


# --------------------------------------------------
# UPLOAD DOCUMENT
# MEMBER 2 → 3A → FAISS
# --------------------------------------------------

@app.post("/api/files/upload")
async def upload_file(
    file: UploadFile = File(...)
):

    # --------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )


    # --------------------------------------------------
    # SUPPORTED FILE TYPES
    # --------------------------------------------------

    supported_extensions = [

        ".pdf",
        ".docx",
        ".txt",
        ".csv",
        ".xlsx",
        ".pptx",
        ".png",
        ".jpg",
        ".jpeg"

    ]


    extension = Path(
        file.filename
    ).suffix.lower()


    if extension not in supported_extensions:

        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}"
        )


    # --------------------------------------------------
    # CREATE UNIQUE FILE ID
    # --------------------------------------------------

    file_id = str(
        uuid.uuid4()
    )


    saved_filename = (
        f"{file_id}{extension}"
    )


    file_path = (
        UPLOAD_DIR / saved_filename
    )


    # --------------------------------------------------
    # SAVE UPLOADED FILE
    # --------------------------------------------------

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    try:

        # ==================================================
        # MEMBER 2
        # EXTRACT DOCUMENT CONTENT
        # ==================================================

        extracted_data = process_file(
            file_path
        )


        # ==================================================
        # 3A
        # NORMALIZE + CREATE CHUNKS
        # ==================================================

        chunks = normalize_document(
            extracted_data,
            file.filename
        )


        if not chunks:

            raise ValueError(
                "No text could be extracted from the document."
            )


        # ==================================================
        # SAVE CHUNKS
        # ==================================================

        save_chunks(
            chunks
        )


        # ==================================================
        # 3A
        # CREATE EMBEDDINGS
        # ==================================================

        texts = [

            chunk["text"]

            for chunk in chunks

        ]


        embeddings = create_embeddings(
            texts
        )


        # ==================================================
        # CREATE FAISS VECTOR STORE
        # ==================================================

        index = create_vector_store(
            embeddings
        )


        # ==================================================
        # SAVE FAISS INDEX
        # ==================================================

        index_path = (
            DATA_DIR / "documents.index"
        )


        faiss.write_index(
            index,
            str(index_path)
        )


    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=(
                f"Document processing failed: "
                f"{str(error)}"
            )

        )


    # --------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------

    return {

        "success": True,

        "file_id": file_id,

        "original_filename": file.filename,

        "file_type": file.content_type,

        "saved_filename": saved_filename,

        "chunks_created": len(chunks),

        "vectors_created": index.ntotal,

        "message": (
            "File processed, chunked and "
            "indexed successfully"
        )

    }


# --------------------------------------------------
# ASK QUESTION
# 3B RETRIEVAL
# --------------------------------------------------

@app.post("/api/ask")
def ask_question(
    request: QuestionRequest
):

    # --------------------------------------------------
    # CHECK QUESTION
    # --------------------------------------------------

    question = request.question.strip()


    if not question:

        raise HTTPException(

            status_code=400,

            detail="Question cannot be empty"

        )


    try:

        # ==================================================
        # 3B
        # RETRIEVE RELEVANT CHUNKS
        # ==================================================

        results = retrieve_information(

            question,

            top_k=5

        )


        # ==================================================
        # RETURN RETRIEVED CONTEXT + EVIDENCE
        # ==================================================

        return {

            "success": True,

            "question": question,

            "results": results,

            "result_count": len(results),

            "message": (
                "Relevant chunks retrieved successfully"
            )

        }


    except FileNotFoundError:

        raise HTTPException(

            status_code=404,

            detail=(
                "No indexed document found. "
                "Please upload a document first."
            )

        )


    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=f"Retrieval failed: {str(error)}"

        )