import json
from pathlib import Path
from src.utils import list_files, load_text_from_pdf, load_text_from_txt, clean_text, chunk_text, smart_split_by_headings
from src.config import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP

DATA_DIR = Path(DATA_DIR)

def ingest_folder(folder: str = None):
    folder = folder or str(DATA_DIR)
    files = list_files(folder)
    docs = []
    for fp in files:
        fp_path = Path(fp)
        try:
            if fp_path.suffix.lower() == ".pdf":
                raw = load_text_from_pdf(fp)
            else:
                raw = load_text_from_txt(fp)
        except Exception as e:
            print(f"Failed to read {fp}: {e}")
            continue
        text = clean_text(raw)
        blocks = smart_split_by_headings(text)
        for i, blk in enumerate(blocks):
            chunks = chunk_text(blk, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
            for j, c in enumerate(chunks):
                docs.append({
                    "source": fp_path.name,
                    "source_path": str(fp_path),
                    "block_id": f"{fp_path.stem}_block{i}",
                    "chunk_id": f"{fp_path.stem}_block{i}_chunk{j}",
                    "text": c
                })
    return docs

if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    docs = ingest_folder()
    out = DATA_DIR / "chunks.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    print(f"Extracted {len(docs)} chunks. Saved to {out}")