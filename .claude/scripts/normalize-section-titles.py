#!/usr/bin/env python3
"""Normalise les titres de section des notes vers leur forme canonique accentuée.

Contexte : le corps des notes est rédigé librement par le LLM pendant
l'ingestion, sans recopie stricte du template. Certaines notes portent donc des
titres de section désaccentués (`## Idee principale`) au lieu de la forme
canonique du template (`## Idée principale`).

Ce script parcourt les notes de tous les thèmes, et pour chaque ligne de titre
`## ...` qui correspond à une variante désaccentuée d'un titre canonique
(dérivé des `.claude/rules/*.md`), la remplace par la forme accentuée.

Seules les lignes de titre sont modifiées — jamais le corps, ni les liens
`[[...]]`.

Usage :
    uv run python .claude/scripts/normalize-section-titles.py            # dry-run
    uv run python .claude/scripts/normalize-section-titles.py --apply    # écrit
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from section_titles import PROJECT_ROOT, build_canonical_map, find_variant

WIKI_THEMES = PROJECT_ROOT / "data" / "wiki" / "themes"

# Mêmes dossiers d'artefacts que lint_wiki.py.
ARTIFACT_DIRS = [
    "notes/atomiques",
    "notes/glossaire",
    "notes/normes",
    "notes/exigences-normatives",
    "notes/processus",
    "notes/objets-metier",
    "notes/regles-metier",
    "notes/regles-reglementaires",
    "notes/habilitations",
    "notes/indicateurs",
    "notes/moc",
    "sources/records",
]

_H2 = re.compile(r"^(## )(?!#)(.+?)([ \t]*)$")


def iter_note_files():
    for theme_dir in sorted(WIKI_THEMES.glob("*")):
        if not theme_dir.is_dir():
            continue
        for rel in ARTIFACT_DIRS:
            folder = theme_dir / rel
            if not folder.exists():
                continue
            for path in sorted(folder.glob("*.md")):
                yield path


def normalize_text(text: str, mapping: dict[str, str]):
    """Retourne (nouveau_texte, [(ancien, nouveau), ...])."""
    changes = []
    out_lines = []
    for line in text.splitlines(keepends=True):
        newline = ""
        stripped = line.rstrip("\n")
        had_nl = line.endswith("\n")
        m = _H2.match(stripped)
        if m:
            title = m.group(2)
            canonical = find_variant(title, mapping)
            if canonical is not None:
                stripped = f"{m.group(1)}{canonical}"
                changes.append((title, canonical))
        newline = stripped + ("\n" if had_nl else "")
        out_lines.append(newline)
    return "".join(out_lines), changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="Écrit les modifications (défaut : dry-run)")
    args = parser.parse_args()

    mapping = build_canonical_map()
    total_files = 0
    total_changes = 0
    touched_files = 0

    for path in iter_note_files():
        total_files += 1
        text = path.read_text(encoding="utf-8")
        new_text, changes = normalize_text(text, mapping)
        if not changes:
            continue
        touched_files += 1
        total_changes += len(changes)
        rel = path.relative_to(PROJECT_ROOT)
        print(f"\n{rel}")
        for old, new in changes:
            print(f"  ## {old}  ->  ## {new}")
        if args.apply:
            path.write_text(new_text, encoding="utf-8")

    mode = "APPLIQUÉ" if args.apply else "DRY-RUN"
    print(f"\n[{mode}] {total_changes} titre(s) dans {touched_files} fichier(s) "
          f"sur {total_files} notes analysées.")
    if not args.apply and total_changes:
        print("Relancer avec --apply pour écrire.")


if __name__ == "__main__":
    main()
