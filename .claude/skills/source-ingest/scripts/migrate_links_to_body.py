#!/usr/bin/env python3
"""
Migration des liens frontmatter → corps de notes.

Pour chaque note :
1. Lit le frontmatter et extrait les IDs dans les champs links: / related_terms: / linked_atomic_notes:
   ainsi que traceability.norm_file (EXN) et relations.related_to/complements/references (NOR, IDs LDE)
2. Vérifie si ces IDs sont déjà dans le corps (section ## Liens contextualisés ou équivalente)
3. Pour les IDs manquants dans le corps, les ajoute dans la section appropriée
4. Supprime les champs concernés du frontmatter

Usage:
    # Audit sec (pas d'écriture) :
    uv run python .claude/skills/source-ingest/scripts/migrate_links_to_body.py --dry-run

    # Migration d'un thème :
    uv run python .claude/skills/source-ingest/scripts/migrate_links_to_body.py --theme maintenance

    # Migration de tous les thèmes :
    uv run python .claude/skills/source-ingest/scripts/migrate_links_to_body.py --theme all
"""
import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WIKI_ROOT = Path.cwd() / "data" / "wiki"
VALID_THEMES = json.loads((WIKI_ROOT / "themes.json").read_text())

# ─── Champs frontmatter à supprimer par type ───────────────────────────────

# Blocs entiers à supprimer (clé de niveau racine + son contenu multi-lignes)
BLOCKS_TO_REMOVE = [
    "links",            # ATO, PRO, OBJ, BRL, IND, EXN, HAB, REG
    "related_terms",    # GLO
    "linked_atomic_notes",  # GLO (liste simple)
]

# Sous-champs de traceability: à supprimer (EXN)
TRACEABILITY_FIELDS_TO_REMOVE = ["norm_file"]

# Sous-champs de relations: à supprimer si valeur = ID LDE (NOR)
NOR_RELATION_FIELDS_TO_MIGRATE = ["related_to", "complements", "references"]

# ─── Sections cibles dans le corps par type ───────────────────────────────

# Section par défaut si aucune section dédiée n'existe
DEFAULT_LINK_SECTION = "## Liens contextualisés"

# Sections terminales après lesquelles on n'insère pas
TERMINAL_SECTIONS = [
    "## Règles", "## Passe terminologique finale",
    "## Critères concrets d'inclusion", "## Notes qui pointent ici",
    "## Validation atomique",
]


# ─── Parsing frontmatter ──────────────────────────────────────────────────

def split_frontmatter(text: str) -> Tuple[str, str]:
    """Retourne (delim_open, frontmatter_raw, rest_of_file)."""
    if not text.startswith("---"):
        return "", "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", "", text
    fm = text[4:end]          # sans le premier ---\n
    rest = text[end + 4:]     # sans le \n---
    return fm, rest


def remove_link_blocks_from_frontmatter(fm: str) -> Tuple[str, Dict[str, List[str]]]:
    """
    Supprime les blocs links:, related_terms:, linked_atomic_notes: du frontmatter.
    Supprime aussi traceability.norm_file (EXN) et relations.related_to/complements/references
    contenant des IDs LDE (NOR).
    Retourne (nouveau_frontmatter, {field: [ids]}).
    """
    lines = fm.splitlines(keepends=True)
    extracted: dict[str, list[str]] = {}
    result_lines = []
    skip_block = False
    current_block = None
    in_related_terms = False
    related_terms_subfield = None
    in_traceability = False
    in_nor_relations = False
    nor_relations_subfield = None

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Détecter le début du bloc traceability: (EXN)
        if not skip_block and not in_related_terms and not in_traceability and not in_nor_relations:
            if stripped == "traceability:":
                in_traceability = True
                result_lines.append(line)
                i += 1
                continue

        # Détecter le début du bloc relations: (NOR)
        if not skip_block and not in_related_terms and not in_traceability and not in_nor_relations:
            if stripped == "relations:":
                in_nor_relations = True
                result_lines.append(line)
                i += 1
                continue

        # Traiter le bloc traceability: — supprimer norm_file
        if in_traceability:
            # Fin du bloc traceability si ligne sans indentation (nouvelle clé racine)
            if not line.startswith(" ") and stripped and not stripped.startswith("-"):
                in_traceability = False
                # Traiter cette ligne normalement (ne pas sauter)
            else:
                # Sous-champ de traceability
                for field in TRACEABILITY_FIELDS_TO_REMOVE:
                    m = re.match(r'\s+' + field + r':\s*(.*)', line)
                    if m:
                        val = m.group(1).strip().strip('"').strip("'")
                        if val and _looks_like_artifact_id(val):
                            extracted[f"traceability.{field}"] = [val]
                        # Supprimer cette ligne (ne pas l'ajouter à result_lines)
                        i += 1
                        break
                else:
                    result_lines.append(line)
                    i += 1
                continue

        # Traiter le bloc relations: — supprimer related_to/complements/references si IDs LDE
        if in_nor_relations:
            # Fin du bloc relations si ligne sans indentation (nouvelle clé racine)
            if not line.startswith(" ") and stripped and not stripped.startswith("-"):
                in_nor_relations = False
                nor_relations_subfield = None
                # Traiter cette ligne normalement (ne pas sauter)
            else:
                # Détecter un sous-champ à migrer
                matched_nor_field = None
                for field in NOR_RELATION_FIELDS_TO_MIGRATE:
                    m = re.match(r'\s+' + field + r':\s*(.*)', line)
                    if m:
                        matched_nor_field = field
                        inline = m.group(1).strip()
                        ids = _parse_inline_list(inline)
                        lde_ids = [id_ for id_ in ids if _looks_like_artifact_id(id_)]
                        non_lde = [id_ for id_ in ids if not _looks_like_artifact_id(id_)]
                        if lde_ids:
                            extracted[f"relations.{field}"] = lde_ids
                        # Si il y a des valeurs non-LDE, garder la ligne réécrite avec seulement celles-là
                        if non_lde:
                            indent = len(line) - len(line.lstrip())
                            non_lde_str = json.dumps(non_lde, ensure_ascii=False)
                            result_lines.append(" " * indent + f"{field}: {non_lde_str}\n")
                        # Sinon supprimer la ligne entière
                        nor_relations_subfield = field if not inline else None
                        i += 1
                        break
                else:
                    # Ligne de liste sous un sous-champ relations en cours
                    if nor_relations_subfield and stripped.startswith("- "):
                        val = stripped[2:].strip().strip('"').strip("'")
                        if val and _looks_like_artifact_id(val):
                            extracted.setdefault(f"relations.{nor_relations_subfield}", []).append(val)
                            i += 1
                            continue
                        else:
                            # Valeur non-LDE dans liste multi-ligne : garder
                            result_lines.append(line)
                            i += 1
                            continue
                    elif not stripped.startswith("- "):
                        nor_relations_subfield = None
                    result_lines.append(line)
                    i += 1
                continue

        # Détecter le début d'un bloc à supprimer
        if not skip_block and not in_related_terms:
            matched_block = None
            for block in BLOCKS_TO_REMOVE:
                if stripped == f"{block}:" or stripped.startswith(f"{block}: "):
                    matched_block = block
                    break

            if matched_block == "related_terms":
                in_related_terms = True
                current_block = "related_terms"
                i += 1
                continue
            elif matched_block == "linked_atomic_notes":
                # Liste simple inline ou multi-lignes
                inline = stripped[len("linked_atomic_notes:"):].strip()
                ids = _parse_inline_list(inline)
                extracted["linked_atomic_notes"] = ids
                # Sauter les lignes suivantes si c'est une liste multi-lignes
                i += 1
                while i < len(lines) and lines[i].startswith("  ") or (i < len(lines) and lines[i].strip().startswith("- ")):
                    val = lines[i].strip().lstrip("- ").strip().strip('"').strip("'")
                    if val and _looks_like_artifact_id(val):
                        extracted["linked_atomic_notes"].append(val)
                    i += 1
                continue
            elif matched_block == "links":
                skip_block = True
                current_block = "links"
                i += 1
                continue

        if in_related_terms:
            # Sous-champ de related_terms
            sub_match = re.match(r'\s+(broader|narrower|close|contrasted):\s*(.*)', line)
            if sub_match:
                subfield = sub_match.group(1)
                related_terms_subfield = f"related_terms.{subfield}"
                inline = sub_match.group(2).strip()
                ids = _parse_inline_list(inline)
                extracted[related_terms_subfield] = ids
                i += 1
                continue
            # Liste sous un sous-champ
            list_match = re.match(r'\s+- (.+)', line)
            if list_match and related_terms_subfield:
                val = list_match.group(1).strip().strip('"').strip("'")
                # Les related_terms peuvent être des libellés libres, pas forcément des IDs
                extracted.setdefault(related_terms_subfield, []).append(val)
                i += 1
                continue
            # Fin du bloc related_terms : ligne sans indentation qui est une clé YAML
            if not line.startswith(" ") and stripped and not stripped.startswith("-"):
                in_related_terms = False
                related_terms_subfield = None
                # Ne pas sauter cette ligne
            else:
                i += 1
                continue

        if skip_block:
            # Sous-ligne du bloc links: (indentée ou liste)
            if line.startswith("  ") or (stripped.startswith("- ") and current_block):
                if stripped.startswith("- "):
                    # Ligne de liste directe sous links:
                    val = stripped[2:].strip().strip('"').strip("'")
                    if val and _looks_like_artifact_id(val):
                        extracted.setdefault(current_block + "_root", []).append(val)
                else:
                    # Sous-clé du bloc links (ex: glossary_terms:)
                    sub_match = re.match(r'\s+(\w+):\s*(.*)', line)
                    if sub_match:
                        subkey = sub_match.group(1)
                        inline_val = sub_match.group(2).strip()
                        ids = _parse_inline_list(inline_val)
                        extracted[subkey] = ids
                i += 1
                continue
            else:
                # Fin du bloc links
                skip_block = False
                current_block = None
                # Ne pas sauter cette ligne, la traiter normalement

        result_lines.append(line)
        i += 1

    # Nettoyer les lignes vides consécutives en fin de frontmatter
    cleaned = "".join(result_lines).rstrip("\n") + "\n"
    # Supprimer les doubles lignes vides
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    return cleaned, extracted


def _parse_inline_list(s: str) -> list[str]:
    """Parse '[\"id1\", \"id2\"]' ou '[]' en liste."""
    if not s or s == "[]":
        return []
    s = s.strip("[]")
    parts = re.findall(r'["\']([^"\']+)["\']', s)
    return [p for p in parts if p]


def _looks_like_artifact_id(s: str) -> bool:
    return bool(re.match(r'^(ATO|GLO|NOR|PRO|OBJ|BRL|IND|EXN|HAB|REG|SRC|MOC)\d{5}', s))


# ─── Manipulation du corps ────────────────────────────────────────────────

def get_existing_wiki_links(body: str) -> set[str]:
    """Retourne l'ensemble des short_id ([[PREFIXE00000]]) déjà dans le corps."""
    pattern = r'\[\[([A-Z]{2,3}\d{5}[^\]]*)\]\]'
    matches = re.findall(pattern, body)
    result = set()
    for m in matches:
        short = re.match(r'^([A-Z]{2,3}\d{5})', m)
        if short:
            result.add(short.group(1))
    return result


def add_links_to_section(body: str, ids_to_add: list[str], section: str = DEFAULT_LINK_SECTION) -> str:
    """
    Ajoute les IDs manquants dans la section cible du corps.
    Si la section n'existe pas, la crée avant les sections terminales.
    """
    if not ids_to_add:
        return body

    new_entries = "\n".join(f"- [[{id_}]]" for id_ in ids_to_add)

    if section in body:
        # Insérer après le header de section, avant la prochaine section ##
        start = body.find(section)
        after_header = start + len(section)
        # Trouver la fin du contenu de la section
        rest = body[after_header:]
        next_sec = re.search(r'\n## ', rest)
        if next_sec:
            insert_pos = after_header + next_sec.start()
            # Insérer avant la prochaine section
            existing_content = body[after_header:insert_pos].rstrip()
            if existing_content.strip() in ("", "-"):
                new_body = body[:after_header] + "\n\n" + new_entries + "\n" + body[insert_pos:]
            else:
                new_body = body[:insert_pos] + "\n" + new_entries + body[insert_pos:]
        else:
            # Fin du fichier
            new_body = body.rstrip() + "\n" + new_entries + "\n"
        return new_body

    # Section inexistante : créer avant les terminales
    insert_before = None
    for terminal in TERMINAL_SECTIONS:
        pos = body.find(f"\n{terminal}")
        if pos != -1:
            if insert_before is None or pos < insert_before:
                insert_before = pos

    new_section = f"{section}\n\n{new_entries}\n"

    if insert_before is not None:
        return body[:insert_before] + "\n\n" + new_section + body[insert_before + 1:]
    else:
        return body.rstrip() + "\n\n" + new_section


# ─── Traitement fichier ───────────────────────────────────────────────────

def migrate_file(path: Path, dry_run: bool = False) -> dict:
    """
    Migre un fichier. Retourne un rapport.
    """
    text = path.read_text(encoding="utf-8")

    if not text.startswith("---"):
        return {"file": str(path), "action": "skipped", "reason": "no frontmatter"}

    # Séparer frontmatter et corps
    fm, rest = split_frontmatter(text)
    if not fm:
        return {"file": str(path), "action": "skipped", "reason": "no frontmatter"}

    # Extraire et supprimer les blocs de liens du frontmatter
    new_fm, extracted = remove_link_blocks_from_frontmatter(fm)

    if not extracted:
        return {"file": str(path), "action": "skipped", "reason": "no link fields"}

    # Collecter tous les IDs d'artefacts extraits, groupés par section cible
    # Les champs relations.* (NOR) vont dans ### Normes liées, les autres dans ## Liens contextualisés
    ids_by_section: dict[str, list[str]] = {}
    for field, ids in extracted.items():
        if field.startswith("relations."):
            section = "### Normes liées"
        else:
            section = DEFAULT_LINK_SECTION
        for id_ in ids:
            if _looks_like_artifact_id(id_):
                ids_by_section.setdefault(section, []).append(id_)

    # Dédupliquer par section
    seen_global = set()
    unique_by_section: dict[str, list[str]] = {}
    for section, ids in ids_by_section.items():
        for id_ in ids:
            short = re.match(r'^([A-Z]{2,3}\d{5})', id_)
            short_id = short.group(1) if short else id_
            if short_id not in seen_global:
                seen_global.add(short_id)
                unique_by_section.setdefault(section, []).append(id_)

    # Vérifier lesquels sont déjà dans le corps
    existing = get_existing_wiki_links(rest)

    def _is_missing(id_: str) -> bool:
        m = re.match(r'^([A-Z]{2,3}\d{5})', id_)
        short_id = m.group(1) if m else id_
        return short_id not in existing and id_ not in existing

    missing_by_section: dict[str, list[str]] = {
        section: [id_ for id_ in ids if _is_missing(id_)]
        for section, ids in unique_by_section.items()
    }

    # Ajouter les manquants dans le corps, section par section
    new_rest = rest
    for section, missing in missing_by_section.items():
        if missing:
            new_rest = add_links_to_section(new_rest, missing, section)

    # Reconstruire le fichier
    new_text = "---\n" + new_fm.rstrip("\n") + "\n---" + new_rest

    all_missing = [id_ for ids in missing_by_section.values() for id_ in ids]
    action = "migrated" if all_missing else "cleaned"
    report = {
        "file": str(path),
        "action": action,
        "extracted_fields": list(extracted.keys()),
        "ids_added_to_body": all_missing,
        "ids_already_in_body": [
            id_ for ids in unique_by_section.values() for id_ in ids
            if not _is_missing(id_)
        ],
    }

    if not dry_run and new_text != text:
        path.write_text(new_text, encoding="utf-8")

    return report


# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Migration des liens frontmatter → corps")
    parser.add_argument("--theme", default="all", help="Thème à traiter (défaut: all)")
    parser.add_argument("--dry-run", action="store_true", help="Simulation sans écriture")
    args = parser.parse_args()

    themes = VALID_THEMES if args.theme == "all" else [args.theme]

    if args.dry_run:
        print("Mode DRY-RUN — aucune écriture.")

    total_migrated = 0
    total_cleaned = 0
    total_skipped = 0

    for theme in themes:
        theme_root = WIKI_ROOT / "themes" / theme / "notes"
        if not theme_root.exists():
            print(f"  [{theme}] Pas de dossier notes/, ignoré.")
            continue

        print(f"\n[{theme}]")
        for md_file in sorted(theme_root.rglob("*.md")):
            report = migrate_file(md_file, dry_run=args.dry_run)
            if report["action"] == "migrated":
                total_migrated += 1
                added = report.get("ids_added_to_body", [])
                print(f"  MIGRÉ  {md_file.name} (+{len(added)} liens)")
            elif report["action"] == "cleaned":
                total_cleaned += 1
                print(f"  NETTOYÉ {md_file.name} (frontmatter purgé, corps déjà complet)")
            else:
                total_skipped += 1

    print(f"\n{'[DRY-RUN] ' if args.dry_run else ''}Terminé.")
    print(f"  Migrés (liens ajoutés au corps) : {total_migrated}")
    print(f"  Nettoyés (frontmatter purgé)    : {total_cleaned}")
    print(f"  Ignorés (pas de liens FM)        : {total_skipped}")


if __name__ == "__main__":
    main()
