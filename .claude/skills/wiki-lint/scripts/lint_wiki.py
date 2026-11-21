#!/usr/bin/env python3
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

WIKI_ROOT = Path.cwd() / "data" / "wiki"
VALID_THEMES = json.loads((WIKI_ROOT / "themes.json").read_text())

# Module partagé : table canonique des titres de section dérivée des règles.
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from section_titles import build_canonical_map, find_variant

SECTION_TITLE_MAP = build_canonical_map()
_H2_LINE = re.compile(r"^## (?!#)(.+?)[ \t]*$", re.MULTILINE)

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

def has_frontmatter(text):
    return text.startswith("---") and "\n---" in text[3:]

def get_field(text, field):
    m = re.search(rf"^{field}:\s*['\"]?([^'\"\n]+)", text, re.MULTILINE)
    return m.group(1).strip() if m else ""

ID_PREFIXES = ["SRC", "ATO", "GLO", "NOR", "EXN", "PRO", "OBJ", "BRL", "REG", "HAB", "IND", "MOC"]
ID_PATTERN = re.compile(r"^(" + "|".join(ID_PREFIXES) + r")\d{5}$")


def build_slug_index(ROOT):
    """Build a set of valid [[ID-slug]] stems (filename without .md) from all artifact dirs."""
    slugs = set()
    for rel in ARTIFACT_DIRS:
        folder = ROOT / rel
        if not folder.exists():
            continue
        for path in folder.glob("*.md"):
            slugs.add(path.stem)
    return slugs


def check_section_titles(text, path, issues):
    """Signale les titres de section non conformes au template (ex. accents
    manquants : `## Idee principale` au lieu de `## Idée principale`)."""
    for m in _H2_LINE.finditer(text):
        title = m.group(1).strip()
        canonical = find_variant(title, SECTION_TITLE_MAP)
        if canonical is not None:
            issues.append((path, "section_title_variant",
                           f"Titre de section non conforme : ## {title} — attendu : ## {canonical}"))


def check_links(text, path, slug_index, issues):
    """Check all [[...]] links in a file."""
    for m in re.finditer(r"\[\[([^\]]+)\]\]", text):
        target = m.group(1).strip()
        if ID_PATTERN.match(target):
            issues.append((path, "link_bare_id", f"Lien sans slug : [[{target}]] — utiliser [[{target}-slug]]"))
        elif re.match(r"^(" + "|".join(ID_PREFIXES) + r")\d{5}-", target):
            if target not in slug_index:
                issues.append((path, "link_broken", f"Lien cassé : [[{target}]] — fichier introuvable"))


def main():
    parser = argparse.ArgumentParser(description="Lint du wiki")
    parser.add_argument("--theme", default="maintenance", choices=VALID_THEMES,
                        help="Thème cible (défaut : maintenance)")
    args = parser.parse_args()

    ROOT = WIKI_ROOT / "themes" / args.theme
    slug_index = build_slug_index(ROOT)
    issues = []
    for rel in ARTIFACT_DIRS:
        folder = ROOT / rel
        if not folder.exists():
            continue
        for path in folder.glob("*.md"):
            text = path.read_text(encoding="utf-8", errors="replace")
            if not has_frontmatter(text):
                issues.append((path, "missing_frontmatter", "Frontmatter absent"))
                continue
            uid = get_field(text, "uid")
            id_ = get_field(text, "id")
            if not uid:
                issues.append((path, "missing_uid", "UID absent"))
            if not id_:
                issues.append((path, "missing_id", "ID absent"))
            if id_ and not path.name.startswith(id_):
                issues.append((path, "filename_id_mismatch", "Le nom de fichier ne commence pas par l'ID"))

            check_links(text, path, slug_index, issues)
            check_section_titles(text, path, issues)

            if "notes/atomiques" in rel:
                words = len(re.findall(r"\w+", text))
                if words > 1200:
                    issues.append((path, "atomic_note_too_long", f"Note atomique longue : {words} mots"))

    today = datetime.date.today().isoformat()
    out_dir = Path.cwd() / "data/generated/logs" / "wiki" / args.theme / "lint"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{today}-lint-report.md"

    cwd = Path.cwd()
    lines = [f"# Rapport lint — {today}", ""]
    if not issues:
        lines.append("Aucun problème détecté.")
    else:
        for path, code, msg in issues:
            try:
                rel = path.relative_to(cwd)
            except ValueError:
                rel = path
            lines.append(f"- `{rel}` — {code} — {msg}")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out)

if __name__ == "__main__":
    main()
