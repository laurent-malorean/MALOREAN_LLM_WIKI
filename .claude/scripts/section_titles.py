#!/usr/bin/env python3
"""Table canonique des titres de section, dérivée des templates.

Les templates de chaque type de note sont les titres `## ...` présents dans les
fichiers `.claude/rules/*.md`. La forme canonique attendue dans le corps des
notes est la forme accentuée de ces titres.

Ce module construit une correspondance `forme désaccentuée -> forme canonique`
utilisée à la fois par la normalisation one-shot (normalize-section-titles.py)
et par le contrôle lint (`section_title_variant`).

Principe :
- on lit tous les titres de niveau 2 (`## ...`) des fichiers de règles ;
- la clé est la forme désaccentuée (et normalisée en casse/espaces) du titre ;
- la valeur est la forme accentuée canonique.

Un titre de note est signalé comme variante non conforme si sa forme
désaccentuée matche une clé ET que le titre diffère de la forme canonique
(typiquement : accents manquants).

Les collisions (deux titres canoniques partageant la même forme désaccentuée,
ex. une variante accentuée et une non accentuée présentes toutes deux dans les
règles) sont écartées : on ne peut pas décider mécaniquement laquelle est
canonique, donc on ne corrige pas ces titres.
"""
import re
import unicodedata
from pathlib import Path

# Racine du projet : ce fichier est dans .claude/scripts/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = PROJECT_ROOT / ".claude" / "rules"

_H2 = re.compile(r"^## (?!#)(.+?)\s*$")


def strip_accents(s: str) -> str:
    """Retourne la chaîne sans diacritiques (NFD + suppression des marques)."""
    nfd = unicodedata.normalize("NFD", s)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


def _key(title: str) -> str:
    """Clé de comparaison : sans accents, minuscules, espaces normalisés."""
    return re.sub(r"\s+", " ", strip_accents(title).casefold()).strip()


def _collect_canonical_titles(rules_dir: Path = RULES_DIR) -> set[str]:
    titles: set[str] = set()
    for path in sorted(rules_dir.glob("*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            m = _H2.match(line)
            if m:
                titles.add(m.group(1).strip())
    return titles


def build_canonical_map(rules_dir: Path = RULES_DIR) -> dict[str, str]:
    """Construit {clé désaccentuée -> titre canonique accentué}.

    Une clé n'est retenue que si elle correspond à un titre canonique contenant
    au moins un accent (sinon il n'y a rien à corriger) et qu'aucune collision
    n'existe sur cette clé.
    """
    titles = _collect_canonical_titles(rules_dir)
    by_key: dict[str, set[str]] = {}
    for t in titles:
        by_key.setdefault(_key(t), set()).add(t)

    mapping: dict[str, str] = {}
    for key, variants in by_key.items():
        # Titres accentués (différents de leur propre forme désaccentuée).
        accented = {t for t in variants if strip_accents(t) != t}
        if len(accented) != 1:
            # 0 accentué : rien à corriger. >1 : collision ambiguë -> on écarte.
            continue
        mapping[key] = next(iter(accented))
    return mapping


def find_variant(title: str, mapping: dict[str, str]) -> str | None:
    """Retourne la forme canonique si `title` est une variante non conforme,
    sinon None."""
    canonical = mapping.get(_key(title.strip()))
    if canonical is None:
        return None
    if title.strip() == canonical:
        return None
    return canonical


if __name__ == "__main__":
    m = build_canonical_map()
    print(f"{len(m)} titres canoniques accentués dérivés des règles :\n")
    for key, canonical in sorted(m.items(), key=lambda kv: kv[1]):
        print(f"  {key!r:45} -> {canonical!r}")
