from typing import List
from pathlib import Path
import re
import pdfplumber

def list_files(folder: str, exts=(".pdf", ".txt")) -> List[str]:
    p = Path(folder)
    files = []
    for ext in exts:
        files.extend([str(f) for f in p.glob(f"*{ext}")])
    return files

def load_text_from_pdf(path: str) -> str:
    text_pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_pages.append(t)
    return "\n".join(text_pages)

def load_text_from_txt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

def clean_text(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r'\n{2,}', '\n\n', s)
    s = re.sub(r'[ \t]{2,}', ' ', s)
    return s.strip()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

def smart_split_by_headings(text: str) -> List[str]:
    lines = text.splitlines()
    blocks = []
    cur = []
    for line in lines:
        if len(line.strip()) == 0:
            if cur:
                blocks.append("\n".join(cur).strip())
                cur = []
            continue
        if line.strip().isupper() or line.strip().endswith(":"):
            if cur:
                blocks.append("\n".join(cur).strip())
            cur = [line]
        else:
            cur.append(line)
    if cur:
        blocks.append("\n".join(cur).strip())
    return blocks