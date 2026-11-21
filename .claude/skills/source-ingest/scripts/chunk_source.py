#!/usr/bin/env python3
from pathlib import Path
import sys
import json
import re

TARGET_WORDS = 3500
MAX_WORDS = 6000
OVERLAP_PARAGRAPHS = 3

def split_paragraphs(text: str):
    parts = re.split(r"\n\s*\n", text)
    return [p.strip() for p in parts if p.strip()]

def word_count(text: str) -> int:
    return len(re.findall(r"\w+", text))

def detect_page(text: str):
    matches = re.findall(r"--- PAGE (\d+) ---", text)
    if matches:
        return int(matches[0]), int(matches[-1])
    return None, None

def make_chunks(paragraphs):
    chunks = []
    current = []
    current_words = 0

    for p in paragraphs:
        wc = word_count(p)

        if current and current_words + wc > TARGET_WORDS:
            chunk_text = "\n\n".join(current)
            chunks.append(chunk_text)

            overlap = current[-OVERLAP_PARAGRAPHS:] if len(current) > OVERLAP_PARAGRAPHS else current
            current = overlap[:]
            current_words = word_count("\n\n".join(current))

        current.append(p)
        current_words += wc

        if current_words > MAX_WORDS:
            chunk_text = "\n\n".join(current)
            chunks.append(chunk_text)
            current = []
            current_words = 0

    if current:
        chunks.append("\n\n".join(current))

    return chunks

def main():
    if len(sys.argv) < 3:
        print("Usage: chunk_source.py source.txt output_chunks.json", file=sys.stderr)
        sys.exit(1)

    txt_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    text = txt_path.read_text(encoding="utf-8", errors="replace")
    paragraphs = split_paragraphs(text)
    chunks = make_chunks(paragraphs)

    manifest = []
    cursor = 0

    for i, chunk in enumerate(chunks, start=1):
        start = text.find(chunk[:100], cursor)
        if start == -1:
            start = cursor
        end = start + len(chunk)
        cursor = end

        start_page, end_page = detect_page(chunk)

        manifest.append({
            "chunk_id": i,
            "start_page": start_page,
            "end_page": end_page,
            "start_char": start,
            "end_char": end,
            "word_count": word_count(chunk),
            "status": "pending",
            "artifacts_created": [],
            "artifacts_updated": [],
            "notes": ""
        })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    chunks_dir = out_path.parent / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    for i, chunk in enumerate(chunks, start=1):
        (chunks_dir / f"chunk-{i:04d}.txt").write_text(chunk, encoding="utf-8")

    print(f"Created {len(chunks)} chunks")

if __name__ == "__main__":
    main()
