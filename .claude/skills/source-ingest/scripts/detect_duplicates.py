#!/usr/bin/env python3
import argparse
import difflib
import json
from pathlib import Path

WIKI_ROOT = Path.cwd() / "data" / "wiki"
VALID_THEMES = json.loads((WIKI_ROOT / "themes.json").read_text())

def main():
    parser = argparse.ArgumentParser(description="Détecter les doublons potentiels")
    parser.add_argument("--theme", default="maintenance", choices=VALID_THEMES,
                        help="Thème cible (défaut : maintenance)")
    args = parser.parse_args()

    THEME_ROOT = WIKI_ROOT / "themes" / args.theme
    index_path = Path.cwd() / "data" / "generated" / "indexes" / args.theme / "artifacts.index.json"
    if not index_path.exists():
        print("No artifacts index found")
        return

    artifacts = json.loads(index_path.read_text(encoding="utf-8"))
    candidates = []

    for i, a in enumerate(artifacts):
        for b in artifacts[i + 1:]:
            if a.get("type") != b.get("type"):
                continue
            title_a = a.get("title", "")
            title_b = b.get("title", "")
            score = difflib.SequenceMatcher(None, title_a.lower(), title_b.lower()).ratio()
            if score >= 0.82:
                candidates.append({
                    "a": a,
                    "b": b,
                    "score": round(score, 3),
                    "status": "candidate"
                })

    out = Path.cwd() / "data" / "generated" / "indexes" / args.theme / "duplicates-candidates.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(candidates, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Duplicate candidates: {len(candidates)}")

if __name__ == "__main__":
    main()
