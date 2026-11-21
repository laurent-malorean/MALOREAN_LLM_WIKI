#!/usr/bin/env python3
"""
Reconstruit data/generated/indexes/{theme}/sources.index.json depuis les fiches sources/records/*.md du thème.

Usage:
    uv run python .claude/skills/source-ingest/scripts/update_sources_index.py --theme product_management
"""
import argparse
import json
import re
from pathlib import Path

WIKI_ROOT = Path.cwd() / "data" / "wiki"
VALID_THEMES = json.loads((WIKI_ROOT / "themes.json").read_text())


def parse_frontmatter_blocks(text: str) -> dict:
    """Parse le frontmatter YAML avec blocs imbriqués (source:, files:, processing:)."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = text[3:end].strip()

    data = {}
    current_block = None

    for line in fm.splitlines():
        # Ligne vide
        if not line.strip():
            continue

        # Bloc imbriqué (ex: "source:", "files:", "processing:")
        if re.match(r"^[a-z_]+:\s*$", line):
            current_block = line.strip().rstrip(":")
            data[current_block] = {}
            continue

        # Propriété dans un bloc imbriqué (2 espaces d'indentation)
        if current_block and line.startswith("  ") and not line.startswith("   "):
            inner = line.strip()
            if ":" in inner:
                key, value = inner.split(":", 1)
                value = value.strip().strip('"').strip("'")
                # Valeur liste inline ex: ["a", "b"]
                if value.startswith("[") and value.endswith("]"):
                    inner_list = value[1:-1]
                    if inner_list.strip():
                        items = [i.strip().strip('"').strip("'") for i in inner_list.split(",")]
                        value = [i for i in items if i]
                    else:
                        value = []
                data[current_block][key.strip()] = value
            continue

        # Propriété racine
        if ":" in line and not line.startswith(" "):
            current_block = None
            key, value = line.split(":", 1)
            value = value.strip().strip('"').strip("'")
            if value.startswith("[") and value.endswith("]"):
                inner_list = value[1:-1]
                if inner_list.strip():
                    items = [i.strip().strip('"').strip("'") for i in inner_list.split(",")]
                    value = [i for i in items if i]
                else:
                    value = []
            data[key.strip()] = value

    return data


def record_to_entry(path: Path, theme_root: Path):
    """Convertit une fiche source record en entrée d'index."""
    text = path.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter_blocks(text)

    uid = fm.get("uid", "")
    src_id = fm.get("id", "")
    status = fm.get("status", "added")

    if not src_id:
        return None

    source = fm.get("source", {})
    files = fm.get("files", {})
    processing = fm.get("processing", {})

    ingested_raw = processing.get("ingested", False)
    ingested = ingested_raw is True or str(ingested_raw).lower() == "true"

    ingestion_coverage_raw = processing.get("ingestion_coverage", 0)
    try:
        ingestion_coverage = int(ingestion_coverage_raw)
    except (ValueError, TypeError):
        ingestion_coverage = 0

    domain = source.get("domain", [])
    if isinstance(domain, str):
        domain = [domain] if domain else []

    entry = {
        "id": src_id,
        "uid": uid,
        "title": source.get("title", ""),
        "author": source.get("author", ""),
        "source_type": source.get("source_type", ""),
        "language": source.get("language", ""),
        "domain": domain,
        "status": status,
        "ingested": ingested,
        "ingestion_status": processing.get("ingestion_status", "not_started"),
        "ingestion_coverage": ingestion_coverage,
        "record": str(path.relative_to(theme_root)),
        "raw_pdf": files.get("raw_pdf", ""),
        "raw_txt": files.get("raw_txt", ""),
    }
    return entry


def main():
    parser = argparse.ArgumentParser(description="Reconstruire sources.index.json")
    parser.add_argument("--theme", default="maintenance", choices=VALID_THEMES,
                        help="Thème cible (défaut : maintenance)")
    args = parser.parse_args()

    theme_root = WIKI_ROOT / "themes" / args.theme
    records_dir = theme_root / "sources" / "records"

    if not records_dir.exists():
        print(f"Dossier introuvable : {records_dir}")
        return

    entries = []
    for path in sorted(records_dir.glob("*.md")):
        entry = record_to_entry(path, theme_root)
        if entry:
            entries.append(entry)

    # Trier par id
    entries.sort(key=lambda e: e["id"])

    out = Path.cwd() / "data" / "generated" / "indexes" / args.theme / "sources.index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Indexed {len(entries)} sources → {out}")

    # Résumé
    ingested = [e for e in entries if e["ingested"]]
    pending = [e for e in entries if not e["ingested"]]
    print(f"  Ingérées   : {len(ingested)} ({', '.join(e['id'] for e in ingested)})")
    print(f"  En attente : {len(pending)} ({', '.join(e['id'] for e in pending)})")


if __name__ == "__main__":
    main()
