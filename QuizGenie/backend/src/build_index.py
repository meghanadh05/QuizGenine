from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
from pathlib import Path
from src.config import INDEX_DIR, EMBED_MODEL
from src.ingest import ingest_folder

INDEX_DIR = Path(INDEX_DIR)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

def build():
    docs = ingest_folder()
    texts = [d["text"] for d in docs]
    model = SentenceTransformer(EMBED_MODEL)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    dim = embeddings.shape[1]
    # use cosine via normalized inner product
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_DIR / "faiss.index"))
    with open(INDEX_DIR / "meta.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    print("Index and metadata saved to indices/")

if __name__ == "__main__":
    build()