from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
from pathlib import Path
from src.config import INDEX_DIR, EMBED_MODEL
import os

INDEX_DIR = Path(INDEX_DIR)

def load_index():
    index = faiss.read_index(str(INDEX_DIR / "faiss.index"))
    with open(INDEX_DIR / "meta.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    return index, meta

def retrieve(query: str, top_k=5):
    model = SentenceTransformer(EMBED_MODEL)
    q_emb = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)
    index, meta = load_index()
    distances, indices = index.search(q_emb, top_k)
    results = []
    for idx, score in zip(indices[0], distances[0]):
        if idx < len(meta):
            results.append((meta[idx], float(score)))
    return results