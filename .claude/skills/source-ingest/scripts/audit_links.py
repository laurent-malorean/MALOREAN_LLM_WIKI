#!/usr/bin/env python3
"""
Audit des liens en frontmatter vs corps de notes.

Parcourt tous les fichiers Markdown du wiki et détecte :
- les blocs links: / related_terms: / linked_atomic_notes: dans le frontmatter
- la présence ou absence des mêmes IDs dans le corps de la note

Produit un rapport JSON : data/generated/logs/wiki/migrate-links-audit.json

Usage:
    uv run python .claude/skills/source-ingest/scripts/audit_links.py
    uv run python .claude/skills/source-ingest/scripts/audit_links.py --theme ai_data_science
"""
import argparse
import json
import re
from pathlib import Path
from typing import Optional

WIKI_ROOT = Path.cwd() / "data" / "wiki"
VALID_THEMES = json.loads((WIKI_ROOT / "themes.json").read_text())

# Champs de frontmatter contenant des liens inter-artefacts (à migrer vers le corps)
LINK_FIELDS = [
    "parents", "related", "contrasts", "examples", "consequences",  # ATO
    "linked_atomic_notes",                                           # GLO
    "glossary_terms", "domain_objects", "business_rules", "norms",  # PRO, OBJ, BRL, IND, EXN
    "requirements", "indicators", "atomic_notes", "processes",
    "evidence", "related_requirements",
    "regulatory_texts", "habilitations", "normative_requirements",  # HAB, REG
    "related_regulatory",
]

# Champs GLO de related_terms (sous-blocs)
RELATED_TERMS_SUBFIELDS = ["broader", "narrower", "close", "contrasted"]

# Sous-champs de traceability: à auditer (EXN)
TRACEABILITY_LINK_FIELDS = ["norm_file"]

# Sous-champs de relations: à auditer si valeur = ID LDE (NOR)
NOR_RELATION_FIELDS = ["related_to", "complements", "references"]


def extract_frontmatter(text: str) -> tuple[str, str]:
    """Retourne (frontmatter_raw, body)."""
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    return text[3:end].strip(), text[end + 4:].strip()


def extract_ids_from_frontmatter(fm: str) -> dict[str, list[str]]:
    """
    Extrait les IDs d'artefacts depuis le frontmatter.
    Retourne un dict {field_name: [id1, id2, ...]}
    Couvre aussi traceability.norm_file (EXN) et relations.related_to/complements/references (NOR).
    """
    results = {}
    lines = fm.splitlines()
    current_field = None
    in_related_terms = False
    in_traceability = False
    in_nor_relations = False
    nor_relations_subfield = None

    for line in lines:
        stripped = line.strip()

        # Détecter le début du bloc traceability:
        if stripped == "traceability:":
            in_traceability = True
            in_nor_relations = False
            current_field = None
            continue

        # Détecter le début du bloc relations:
        if stripped == "relations:":
            in_nor_relations = True
            in_traceability = False
            current_field = None
            continue

        # Traiter le bloc traceability:
        if in_traceability:
            if not line.startswith(" ") and stripped and not stripped.startswith("-"):
                in_traceability = False
            else:
                for field in TRACEABILITY_LINK_FIELDS:
                    m = re.match(r'\s+' + field + r':\s*(.*)', line)
                    if m:
                        val = m.group(1).strip().strip('"').strip("'")
                        if val and _looks_like_artifact_id(val):
                            results[f"traceability.{field}"] = [val]
                        break
                continue

        # Traiter le bloc relations:
        if in_nor_relations:
            if not line.startswith(" ") and stripped and not stripped.startswith("-"):
                in_nor_relations = False
                nor_relations_subfield = None
            else:
                matched = False
                for field in NOR_RELATION_FIELDS:
                    m = re.match(r'\s+' + field + r':\s*(.*)', line)
                    if m:
                        nor_relations_subfield = field
                        inline = m.group(1).strip()
                        ids = [id_ for id_ in _parse_inline_list_raw(inline) if _looks_like_artifact_id(id_)]
                        if ids:
                            results[f"relations.{field}"] = ids
                        matched = True
                        break
                if not matched and nor_relations_subfield and stripped.startswith("- "):
                    val = stripped[2:].strip().strip('"').strip("'")
                    if val and _looks_like_artifact_id(val):
                        results.setdefault(f"relations.{nor_relations_subfield}", []).append(val)
                elif not stripped.startswith("- "):
                    nor_relations_subfield = None
                continue

        # Détecter related_terms: (bloc GLO)
        if stripped == "related_terms:":
            in_related_terms = True
            continue

        if in_related_terms:
            # Sous-champ de related_terms
            for sub in RELATED_TERMS_SUBFIELDS:
                if stripped.startswith(f"{sub}:"):
                    current_field = f"related_terms.{sub}"
                    # Valeur inline: broader: ["foo", "bar"]
                    inline = stripped[len(sub) + 1:].strip()
                    ids = _parse_inline_list(inline)
                    if ids:
                        results[current_field] = ids
                        current_field = None
                    break
            else:
                # Fin du bloc related_terms si on rencontre une ligne sans indentation
                if not line.startswith(" ") and stripped and not stripped.startswith("-"):
                    in_related_terms = False

        # Détecter les champs de liens connus
        for field in LINK_FIELDS:
            if stripped.startswith(f"{field}:"):
                current_field = field
                inline = stripped[len(field) + 1:].strip()
                ids = _parse_inline_list(inline)
                if ids:
                    results[field] = ids
                    current_field = None
                break
        else:
            # Ligne de liste sous un champ courant
            if current_field and stripped.startswith("- "):
                value = stripped[2:].strip().strip('"').strip("'")
                if value and _looks_like_artifact_id(value):
                    results.setdefault(current_field, []).append(value)
            elif stripped and not stripped.startswith("-") and not stripped.startswith(" "):
                # Nouvelle clé de niveau racine, reset
                current_field = None

    return results


def _parse_inline_list(s: str) -> list[str]:
    """Parse '[\"id1\", \"id2\"]' ou '[]' en liste, filtre les IDs artefacts."""
    if not s or s == "[]":
        return []
    s = s.strip("[]")
    parts = re.findall(r'["\']([^"\']+)["\']', s)
    return [p for p in parts if _looks_like_artifact_id(p)]


def _parse_inline_list_raw(s: str) -> list[str]:
    """Parse '[\"val1\", \"val2\"]' ou '[]' en liste, sans filtrage."""
    if not s or s == "[]":
        return []
    s = s.strip("[]")
    parts = re.findall(r'["\']([^"\']+)["\']', s)
    return parts


def _looks_like_artifact_id(s: str) -> bool:
    """Vérifie qu'une chaîne ressemble à un ID d'artefact (ATO00001 ou ATO00001-slug)."""
    return bool(re.match(r'^(ATO|GLO|NOR|PRO|OBJ|BRL|IND|EXN|HAB|REG|SRC|MOC|IND)\d{5}', s))


def extract_wiki_links_from_body(body: str) -> set[str]:
    """Extrait tous les [[ID-slug]] du corps de la note."""
    pattern = r'\[\[([A-Z]{2,3}\d{5}[^\]]*)\]\]'
    matches = re.findall(pattern, body)
    # Normalise : extrait juste le préfixe+numéro pour comparaison
    ids = set()
    for m in matches:
        # Conserve l'ID complet avec slug
        ids.add(m.strip())
        # Ajoute aussi la version courte (préfixe+numéro) pour comparaison souple
        short = re.match(r'^([A-Z]{2,3}\d{5})', m)
        if short:
            ids.add(short.group(1))
    return ids


def audit_file(path: Path) -> Optional[dict]:
    """Audite un fichier et retourne un rapport ou None si rien à signaler."""
    text = path.read_text(encoding="utf-8")
    fm, body = extract_frontmatter(text)
    if not fm:
        return None

    fm_ids = extract_ids_from_frontmatter(fm)
    if not fm_ids:
        return None

    body_ids = extract_wiki_links_from_body(body)

    # Classifier chaque ID : présent dans le corps ou non
    details = {}
    all_missing = []
    all_present = []

    for field, ids in fm_ids.items():
        missing = []
        present = []
        for id_ in ids:
            short = re.match(r'^([A-Z]{2,3}\d{5})', id_)
            short_id = short.group(1) if short else id_
            if short_id in body_ids or id_ in body_ids:
                present.append(id_)
            else:
                missing.append(id_)
        if ids:
            details[field] = {"ids": ids, "in_body": present, "missing_from_body": missing}
            all_missing.extend(missing)
            all_present.extend(present)

    if not details:
        return None

    action = "already_done" if not all_missing else ("migrate" if not all_present else "partial")

    return {
        "file": str(path),
        "type": _detect_type(fm),
        "frontmatter_links": details,
        "action": action,
        "missing_count": len(all_missing),
        "present_count": len(all_present),
    }


def _detect_type(fm: str) -> str:
    m = re.search(r'^type:\s*["\']?(\w+)["\']?', fm, re.MULTILINE)
    return m.group(1) if m else "unknown"


def main():
    parser = argparse.ArgumentParser(description="Audit des liens frontmatter → corps")
    parser.add_argument("--theme", default=None, help="Thème à auditer (défaut: tous)")
    args = parser.parse_args()

    themes = [args.theme] if args.theme else VALID_THEMES

    results = []
    total_files = 0
    total_with_fm_links = 0
    total_missing = 0

    for theme in themes:
        theme_root = WIKI_ROOT / "themes" / theme / "notes"
        if not theme_root.exists():
            continue
        for md_file in sorted(theme_root.rglob("*.md")):
            total_files += 1
            report = audit_file(md_file)
            if report:
                total_with_fm_links += 1
                total_missing += report["missing_count"]
                results.append(report)

    # Rapport par action
    by_action = {"migrate": [], "partial": [], "already_done": []}
    for r in results:
        by_action.get(r["action"], []).append(r["file"])

    output = {
        "summary": {
            "total_files_scanned": total_files,
            "files_with_frontmatter_links": total_with_fm_links,
            "files_to_migrate": len(by_action["migrate"]),
            "files_partial": len(by_action["partial"]),
            "files_already_done": len(by_action["already_done"]),
            "total_ids_missing_from_body": total_missing,
        },
        "by_action": by_action,
        "details": results,
    }

    out_path = WIKI_ROOT.parent / "generated" / "logs" / "wiki" / "migrate-links-audit.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Audit terminé. {total_with_fm_links} fichiers avec liens en frontmatter.")
    print(f"  - À migrer (corps vide) : {len(by_action['migrate'])}")
    print(f"  - Partiels (corps incomplet) : {len(by_action['partial'])}")
    print(f"  - Déjà dans le corps : {len(by_action['already_done'])}")
    print(f"Rapport : {out_path}")


if __name__ == "__main__":
    main()
