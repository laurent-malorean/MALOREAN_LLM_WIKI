#!/usr/bin/env python3
"""
Corrige tous les liens [[ID-slug]] dont le slug ne correspond pas au fichier réel.
Supprime les liens [[ID-slug]] dont l'ID n'existe nulle part.
Usage: uv run python .claude/scripts/fix-broken-slugs.py [--dry-run]
"""
import re
import sys
import unicodedata
from pathlib import Path

WIKI_ROOT = Path.cwd() / "data" / "wiki" / "themes"
DRY_RUN = "--dry-run" in sys.argv

# Construire l'index ID -> slug réel (depuis notes/ et sources/records/)
id_to_slug = {}
for theme_dir in WIKI_ROOT.glob("*/"):
    if theme_dir.name in ["counters.json", "memory"]:
        continue
    for search_dir in [theme_dir / "notes", theme_dir / "sources" / "records"]:
        if not search_dir.exists():
            continue
        for md_file in search_dir.rglob("*.md"):
            m = re.match(r'^([A-Z]{3}\d{5})-(.+)\.md$', md_file.name)
            if m:
                # macOS stocke les noms en NFD : normaliser en NFC (forme des liens)
                id_to_slug[m.group(1)] = unicodedata.normalize("NFC", m.group(2))

print(f"📦 {len(id_to_slug)} artefacts indexés")

link_pattern = re.compile(r'\[\[([A-Z]{3}\d{5})(?:-([^\]|]+))?\]\]')

fixed_files = 0
fixed_links = 0
removed_links = 0

for md_file in WIKI_ROOT.rglob("*.md"):
    try:
        content = md_file.read_text(encoding="utf-8")
    except Exception:
        continue

    new_content = content
    file_changed = False

    for m in link_pattern.finditer(content):
        artifact_id = m.group(1)
        current_slug = m.group(2) or ""
        full_match = f"[[{artifact_id}-{current_slug}]]" if current_slug else f"[[{artifact_id}]]"

        if artifact_id not in id_to_slug:
            new_link = f"`{artifact_id}` *(lien supprimé — artefact inexistant)*"
            new_content = new_content.replace(full_match, new_link, 1)
            file_changed = True
            removed_links += 1
            print(f"  ❌ SUPPRIMÉ {full_match}")
        else:
            correct_slug = id_to_slug[artifact_id]
            correct_link = f"[[{artifact_id}-{correct_slug}]]"
            if unicodedata.normalize("NFC", full_match) != correct_link:
                new_content = new_content.replace(full_match, correct_link, 1)
                file_changed = True
                fixed_links += 1

    if file_changed:
        fixed_files += 1
        if not DRY_RUN:
            md_file.write_text(new_content, encoding="utf-8")

mode = "[DRY RUN] " if DRY_RUN else ""
print(f"\n{mode}✅ Terminé")
print(f"  Fichiers modifiés : {fixed_files}")
print(f"  Liens corrigés (slug) : {fixed_links}")
print(f"  Liens supprimés (ID inexistant) : {removed_links}")
