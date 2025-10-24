# src/api/main.py
import logging
import shutil
import os
import json
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pypdf
from sentence_transformers import SentenceTransformer
import faiss

# We will use the existing generate_quiz function, but we will call it from our new RAG logic
from src.generate_quiz import generate_quiz as call_llm_for_quiz

logger = logging.getLogger("uvicorn.error")
app = FastAPI()

EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

# CORS Middleware
origins = [
    "http://localhost", "http://localhost:8000",
    "http://localhost:5173", "http://127.0.0.1:5173",
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- Helper functions (unchanged) ---

def _read_pdf(file_path: str) -> str:
    try:
        reader = pypdf.PdfReader(file_path)
        text = "".join(page.extract_text() or "" for page in reader.pages)
        return text
    except Exception as e:
        logger.error(f"Error reading PDF {file_path}: {e}")
        return ""

def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    if not text: return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def _embed_chunks(chunks: list[str]) -> np.ndarray:
    embeddings = EMBEDDING_MODEL.encode(chunks, convert_to_numpy=True)
    return embeddings

def _build_and_save_index(embeddings: np.ndarray, chunks: list[str], save_dir: str = "indices"):
    if not os.path.exists(save_dir): os.makedirs(save_dir)
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    faiss.write_index(index, os.path.join(save_dir, "faiss.index"))
    with open(os.path.join(save_dir, "chunks.json"), "w") as f:
        json.dump(chunks, f)

# --- Upload Endpoint (unchanged) ---
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        save_path = f"data/{file.filename}"
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        doc_text = _read_pdf(save_path)
        if not doc_text:
            return JSONResponse(status_code=400, content={"message": "Could not read text from PDF."})
        chunks = _chunk_text(doc_text)
        embeddings = _embed_chunks(chunks)
        _build_and_save_index(embeddings, chunks)
        return JSONResponse(status_code=200, content={"filename": file.filename, "message": f"File processed and indexed successfully. Created {len(chunks)} chunks."})
    except Exception as e:
        logger.exception("Error during file ingestion")
        return JSONResponse(status_code=500, content={"detail": f"An error occurred: {str(e)}"})

# --- Health Check (unchanged) ---
@app.get("/", tags=["health"])
async def root():
    return JSONResponse({"status":"ok", "message":"QuizGenine backend running"})

# --- NEW RAG-POWERED QUIZ GENERATION ENDPOINT ---
@app.post("/generate_quiz")
async def gen_quiz_from_index():
    """
    Generates a quiz by retrieving context from the FAISS index.
    """
    try:
        index_path = "indices/faiss.index"
        chunks_path = "indices/chunks.json"

        if not os.path.exists(index_path) or not os.path.exists(chunks_path):
            return JSONResponse(status_code=404, content={"message": "Index not found. Please upload a document first."})

        # 1. Load the index and chunks
        index = faiss.read_index(index_path)
        with open(chunks_path, "r") as f:
            chunks = json.load(f)

        # 2. Create a query to find relevant context
        query_text = "Generate multiple choice questions covering the key concepts in this document."
        query_embedding = EMBEDDING_MODEL.encode([query_text], convert_to_numpy=True)
        
        # 3. Perform similarity search
        k = 3 # Number of relevant chunks to retrieve
        distances, indices = index.search(query_embedding, k)
        
        retrieved_chunks = [chunks[i] for i in indices[0]]
        context = "\n---\n".join(retrieved_chunks)

        # 4. Augment the prompt and call the LLM
        # We pass the context as the "topic" to the original function
        result = call_llm_for_quiz(topic=context, top_k=10)
        
        return {
            "status": "ok",
            "from_mock": bool(result.get("from_mock")),
            "data": result.get("questions"),
        }
    except Exception as e:
        logger.exception("Unhandled error in /generate_quiz")
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)