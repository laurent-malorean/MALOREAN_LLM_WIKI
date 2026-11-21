#!/usr/bin/env python3
"""
check_links.py — Détecte les liens [[...]] cassés dans le wiki.
Usage : uv run python check_links.py [--theme THEME] [--summary]
"""
import argparse
import json
import re
import sys
from pathlib import Path

WIKI_ROOT = Path(__file__).parent.parent.parent.parent.parent / "data" / "wiki"
VALID_THEMES = json.loads((WIKI_ROOT / "themes.json").read_text())

ARTIFACT_DIRS = [
    "notes/atomiques", "notes/glossaire", "notes/normes",
    "notes/exigences-normatives", "notes/processus", "notes/objets-metier",
    "notes/regles-metier", "notes/indicateurs", "notes/moc",
    "notes/regles-reglementaires", "notes/habilitations", "sources/records",
]
ID_PREFIXES = ["SRC","ATO","GLO","NOR","EXN","PRO","OBJ","BRL","REG","HAB","IND","MOC"]
ID_RE = re.compile(r"^(" + "|".join(ID_PREFIXES) + r")\d{5}")
LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

def main():
    parser = argparse.ArgumentParser(description="Vérification des liens wiki")
    parser.add_argument("--theme", default="maintenance", choices=VALID_THEMES,
                        help="Thème cible (défaut : maintenance)")
    parser.add_argument("--summary", action="store_true",
                        help="Afficher uniquement le résumé")
    args = parser.parse_args()

    ROOT = WIKI_ROOT / "themes" / args.theme

    # Index : tous les stems valides
    valid = set()
    for rel in ARTIFACT_DIRS:
        d = ROOT / rel
        if d.exists():
            for p in d.glob("*.md"):
                valid.add(p.stem)

    broken = {}
    for rel in ARTIFACT_DIRS:
        d = ROOT / rel
        if not d.exists():
            continue
        for md in d.glob("*.md"):
            text = md.read_text(errors="ignore")
            for m in LINK_RE.finditer(text):
                inner = m.group(1).split("|")[0].strip()
                if not ID_RE.match(inner):
                    continue
                if inner not in valid:
                    broken.setdefault(inner, []).append(str(md.relative_to(ROOT)))

    if not broken:
        print("✓ Aucun lien cassé détecté.")
        sys.exit(0)

    total = sum(len(v) for v in broken.values())
    print(f"— {len(broken)} cibles manquantes, {total} occurrences —\n")

    for target in sorted(broken):
        files = broken[target]
        print(f"  [[{target}]]  ({len(files)} occurrence{'s' if len(files)>1 else ''})")
        if not args.summary:
            for f in files:
                print(f"    {f}")

if __name__ == "__main__":
    main()
