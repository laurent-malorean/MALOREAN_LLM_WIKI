#!/usr/bin/env python3
from pathlib import Path
import sys
import re

def normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip() + "\n"

def main():
    if len(sys.argv) < 2:
        print("Usage: normalize_text.py file.txt", file=sys.stderr)
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"TXT not found: {path}", file=sys.stderr)
        sys.exit(2)

    text = path.read_text(encoding="utf-8", errors="replace")
    path.write_text(normalize(text), encoding="utf-8")
    print(f"Normalized: {path}")

if __name__ == "__main__":
    main()
