#!/usr/bin/env python3
from pathlib import Path
import sys
import subprocess

def extract_with_pypdf(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        return ""

    reader = PdfReader(str(pdf_path))
    parts = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        parts.append(f"\n\n--- PAGE {i} ---\n\n{text}")
    return "\n".join(parts).strip()

def extract_with_pdftotext(pdf_path: Path, txt_path: Path) -> bool:
    try:
        subprocess.run(["pdftotext", "-layout", str(pdf_path), str(txt_path)], check=True)
        return txt_path.exists()
    except Exception:
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: pdf_to_text.py input.pdf output.txt", file=sys.stderr)
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    txt_path = Path(sys.argv[2])

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(2)

    text = extract_with_pypdf(pdf_path)

    if text:
        txt_path.parent.mkdir(parents=True, exist_ok=True)
        txt_path.write_text(text, encoding="utf-8")
        print(f"Text extracted with pypdf: {txt_path}")
        sys.exit(0)

    txt_path.parent.mkdir(parents=True, exist_ok=True)
    if extract_with_pdftotext(pdf_path, txt_path):
        print(f"Text extracted with pdftotext: {txt_path}")
        sys.exit(0)

    txt_path.write_text("", encoding="utf-8")
    print("Text extraction failed. Empty TXT created.", file=sys.stderr)
    sys.exit(3)

if __name__ == "__main__":
    main()
