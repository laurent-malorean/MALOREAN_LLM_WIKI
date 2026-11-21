#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

WIKI_ROOT = Path.cwd() / "data" / "wiki"
VALID_THEMES = json.loads((WIKI_ROOT / "themes.json").read_text())

def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = text[3:end].strip()
    data = {}
    for line in fm.splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data

def main():
    parser = argparse.ArgumentParser(description="Reconstruire artifacts.index.json")
    parser.add_argument("--theme", default="maintenance", choices=VALID_THEMES,
                        help="Thème cible (défaut : maintenance)")
    args = parser.parse_args()

    THEME_ROOT = WIKI_ROOT / "themes" / args.theme
    artifacts = []
    folders = [
        THEME_ROOT / "notes" / "atomiques",
        THEME_ROOT / "notes" / "glossaire",
        THEME_ROOT / "notes" / "normes",
        THEME_ROOT / "notes" / "exigences-normatives",
        THEME_ROOT / "notes" / "processus",
        THEME_ROOT / "notes" / "objets-metier",
        THEME_ROOT / "notes" / "regles-metier",
        THEME_ROOT / "notes" / "regles-reglementaires",
        THEME_ROOT / "notes" / "habilitations",
        THEME_ROOT / "notes" / "indicateurs",
        THEME_ROOT / "notes" / "moc",
    ]

    for folder in folders:
        if not folder.exists():
            continue
        for path in folder.glob("*.md"):
            text = path.read_text(encoding="utf-8", errors="replace")
            fm = parse_frontmatter(text)
            title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else path.stem
            artifacts.append({
                "uid": fm.get("uid", ""),
                "id": fm.get("id", ""),
                "type": fm.get("type", ""),
                "title": title,
                "path": str(path.relative_to(Path.cwd())),
                "status": fm.get("status", ""),
                "updated": fm.get("updated", "")
            })

    out = Path.cwd() / "data" / "generated" / "indexes" / args.theme / "artifacts.index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifacts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Indexed {len(artifacts)} artifacts")

if __name__ == "__main__":
    main()
