#!/usr/bin/env python3
"""Dresse la liste des idées déjà présentes dans le wiki, à charger UNE SEULE FOIS.

But : donner à l'agent d'ingestion un contexte anti-duplication compact qu'il lit
au début et garde en tête pour toute la source, au lieu de relire l'index à chaque
idée. C'est le pivot de la méthode séquentielle à mémoire cumulative : on ne
recharge jamais ce contexte, on l'enrichit mentalement au fil des sections.

Sortie : sur stdout (ou --out fichier), une liste lisible
    ATOxxxxx  ::  <titre de la note>
    GLOxxxxx  ::  <terme>
triée par ID, pour le(s) thème(s) demandé(s).

Usage :
    uv run python .claude/skills/source-ingest/scripts/existing_ideas.py \
        --theme marketing [--also product_management] [--out chemin.txt]

Interpréteur : toujours uv run python (voir CLAUDE.md).
Chemins relatifs à la racine du projet.
"""
from pathlib import Path
import argparse
import json
import re
import sys

ROOT = Path.cwd()
WIKI = ROOT / "data" / "wiki"


def _field(fp: Path, *names):
    t = fp.read_text(encoding="utf-8", errors="replace")
    for n in names:
        m = re.search(r'^' + re.escape(n) + r':\s*"?(.*?)"?\s*$', t, re.M)
        if m and m.group(1).strip():
            return m.group(1).strip()
    m = re.search(r"^#\s+(.+)$", t, re.M)
    return m.group(1).strip() if m else fp.stem


def collect(theme: str):
    tdir = WIKI / "themes" / theme
    lines = []
    ad = tdir / "notes" / "atomiques"
    if ad.exists():
        for fp in sorted(ad.glob("ATO*.md")):
            lines.append((fp.stem[:8], "ATO", theme, _field(fp, "title")))
    gd = tdir / "notes" / "glossaire"
    if gd.exists():
        for fp in sorted(gd.glob("GLO*.md")):
            lines.append((fp.stem[:8], "GLO", theme, _field(fp, "term", "title")))
    return lines


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--theme", required=True)
    p.add_argument("--also", nargs="*", default=[],
                   help="thèmes voisins à inclure (anti-dup cross-thème)")
    p.add_argument("--out", help="fichier de sortie (défaut : stdout)")
    args = p.parse_args()

    rows = []
    for th in [args.theme] + args.also:
        rows.extend(collect(th))
    rows.sort(key=lambda r: (r[1], r[0]))

    multi = len(args.also) > 0
    out_lines = []
    for ident, kind, th, label in rows:
        prefix = f"[{th}] " if multi else ""
        out_lines.append(f"{prefix}{ident}  ::  {label}")

    n_ato = sum(1 for r in rows if r[1] == "ATO")
    n_glo = sum(1 for r in rows if r[1] == "GLO")
    header = f"# Idées déjà présentes — {n_ato} ATO, {n_glo} GLO (thèmes : {', '.join([args.theme] + args.also)})\n"
    text = header + "\n".join(out_lines) + "\n"

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"{n_ato} ATO + {n_glo} GLO -> {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
