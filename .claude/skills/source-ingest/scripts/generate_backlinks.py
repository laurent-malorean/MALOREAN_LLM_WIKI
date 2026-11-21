#!/usr/bin/env python3
"""
Génère ou met à jour la section '## Notes qui pointent ici' dans chaque note du wiki.

Parcourt toutes les notes d'un thème, construit la map inverse des [[ID-slug]],
puis met à jour la section dédiée dans chaque fichier cible.

La section est identifiée par le marqueur '## Notes qui pointent ici'.
Si elle n'existe pas, elle est ajoutée avant la dernière section ## Règles
ou en fin de fichier.

Usage:
    uv run python .claude/skills/source-ingest/scripts/generate_backlinks.py --theme ai_data_science
    uv run python .claude/skills/source-ingest/scripts/generate_backlinks.py --theme all
"""
import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WIKI_ROOT = Path.cwd() / "data" / "wiki"
VALID_THEMES = json.loads((WIKI_ROOT / "themes.json").read_text())

SECTION_HEADER = "## Notes qui pointent ici"
# Sections après lesquelles on n'insère pas (fin de note administrative)
TERMINAL_SECTIONS = {"## Règles", "## Passe terminologique finale", "## Critères concrets d'inclusion"}


def extract_frontmatter_end(text: str) -> int:
    """Retourne l'index de fin du frontmatter (après le second ---)."""
    if not text.startswith("---"):
        return 0
    end = text.find("\n---", 3)
    if end == -1:
        return 0
    return end + 4


def get_note_id_and_title(path: Path) -> tuple[str, str]:
    """Extrait l'ID et le titre depuis le nom de fichier."""
    stem = path.stem  # ex: ATO01146-les-mathematiques-...
    m = re.match(r'^([A-Z]{2,3}\d{5})(-.+)?$', stem)
    if m:
        return stem, stem
    return stem, stem


def extract_wiki_links(body: str, source_file_stem: str) -> List[Tuple[str, str]]:
    """
    Extrait tous les [[ID-slug]] du corps d'une note.
    Retourne une liste de (full_link, short_id).
    Exclut les liens vers soi-même.
    """
    pattern = r'\[\[([A-Z]{2,3}\d{5}[^\]]*)\]\]'
    matches = re.findall(pattern, body)
    results = []
    seen = set()
    for m in matches:
        m = m.strip()
        short = re.match(r'^([A-Z]{2,3}\d{5})', m)
        if not short:
            continue
        short_id = short.group(1)
        # Éviter les doublons et les auto-liens
        if m in seen:
            continue
        if source_file_stem.startswith(short_id):
            continue
        seen.add(m)
        results.append((m, short_id))
    return results


def build_backlink_map(theme_root: Path) -> Dict[str, List[Tuple[str, str]]]:
    """
    Construit la map inverse : target_stem → [(source_stem, full_link), ...]
    """
    backlinks: dict[str, list[tuple[str, str]]] = {}
    notes_root = theme_root / "notes"
    if not notes_root.exists():
        return backlinks

    for md_file in sorted(notes_root.rglob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        fm_end = extract_frontmatter_end(text)
        body = text[fm_end:]
        source_stem = md_file.stem

        links = extract_wiki_links(body, source_stem)
        for (full_link, short_id) in links:
            # Cherche le fichier cible pour obtenir son stem complet
            # On index par short_id, on résoudra au moment de l'écriture
            backlinks.setdefault(short_id, []).append((source_stem, full_link))

    return backlinks


def build_stem_index(theme_root: Path) -> Dict[str, Path]:
    """Construit un index short_id → Path pour tous les fichiers du thème."""
    index = {}
    notes_root = theme_root / "notes"
    if not notes_root.exists():
        return index
    for md_file in notes_root.rglob("*.md"):
        stem = md_file.stem
        m = re.match(r'^([A-Z]{2,3}\d{5})', stem)
        if m:
            index[m.group(1)] = md_file
    return index


def format_backlinks_section(sources: List[Tuple[str, str]]) -> str:
    """Formate la section ## Notes qui pointent ici."""
    if not sources:
        return f"{SECTION_HEADER}\n\n-\n"
    lines = [SECTION_HEADER, ""]
    for (source_stem, full_link) in sorted(set(sources), key=lambda x: x[0]):
        lines.append(f"- [[{source_stem}]]")
    lines.append("")
    return "\n".join(lines)


def update_file_backlinks(path: Path, sources: List[Tuple[str, str]]) -> bool:
    """
    Met à jour ou crée la section '## Notes qui pointent ici' dans un fichier.
    Retourne True si le fichier a été modifié.
    """
    text = path.read_text(encoding="utf-8")
    new_section = format_backlinks_section(sources)

    # Cas 1 : la section existe déjà — on la remplace
    if SECTION_HEADER in text:
        # Trouver le début de la section
        start = text.find(SECTION_HEADER)
        # Trouver la prochaine section ##
        rest = text[start + len(SECTION_HEADER):]
        next_section = re.search(r'\n## ', rest)
        if next_section:
            end = start + len(SECTION_HEADER) + next_section.start()
            new_text = text[:start] + new_section + "\n" + text[end + 1:]
        else:
            new_text = text[:start] + new_section
        if new_text == text:
            return False
        path.write_text(new_text, encoding="utf-8")
        return True

    # Cas 2 : la section n'existe pas — on l'insère avant ## Règles ou en fin
    insert_before = None
    for terminal in TERMINAL_SECTIONS:
        pos = text.find(f"\n{terminal}")
        if pos != -1:
            if insert_before is None or pos < insert_before:
                insert_before = pos

    if insert_before is not None:
        new_text = text[:insert_before] + "\n\n" + new_section + text[insert_before:]
    else:
        new_text = text.rstrip() + "\n\n" + new_section

    path.write_text(new_text, encoding="utf-8")
    return True


def process_theme(theme: str) -> dict:
    theme_root = WIKI_ROOT / "themes" / theme
    if not theme_root.exists():
        return {"theme": theme, "status": "skipped", "files_updated": 0}

    print(f"  [{theme}] Construction de la map des backlinks...")
    backlinks = build_backlink_map(theme_root)
    stem_index = build_stem_index(theme_root)

    updated = 0
    for short_id, sources in backlinks.items():
        target_path = stem_index.get(short_id)
        if not target_path:
            continue
        if update_file_backlinks(target_path, sources):
            updated += 1

    # Vider la section dans les notes qui ne sont citées par personne
    for short_id, target_path in stem_index.items():
        if short_id not in backlinks:
            text = target_path.read_text(encoding="utf-8")
            if SECTION_HEADER in text:
                if update_file_backlinks(target_path, []):
                    updated += 1

    print(f"  [{theme}] {updated} fichiers mis à jour.")
    return {"theme": theme, "status": "ok", "files_updated": updated}


def main():
    parser = argparse.ArgumentParser(description="Génère les backlinks dans les notes du wiki")
    parser.add_argument("--theme", default="all", help="Thème à traiter (défaut: all)")
    args = parser.parse_args()

    themes = VALID_THEMES if args.theme == "all" else [args.theme]
    print(f"Génération des backlinks pour : {', '.join(themes)}")

    total_updated = 0
    for theme in themes:
        result = process_theme(theme)
        total_updated += result.get("files_updated", 0)

    print(f"\nTerminé. {total_updated} fichiers mis à jour au total.")


if __name__ == "__main__":
    main()
