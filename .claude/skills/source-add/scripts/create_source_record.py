#!/usr/bin/env python3
import argparse
import datetime
import hashlib
import json
import re
import unicodedata
import uuid
from pathlib import Path

WIKI_ROOT = Path.cwd() / "data" / "wiki"

VALID_THEMES = json.loads((WIKI_ROOT / "themes.json").read_text())

def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "source"

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def next_id(prefix: str) -> str:
    counters_path = WIKI_ROOT / "counters.json"
    counters_path.parent.mkdir(parents=True, exist_ok=True)
    if counters_path.exists():
        counters = json.loads(counters_path.read_text(encoding="utf-8"))
    else:
        counters = {}
    counters[prefix] = int(counters.get(prefix, 0)) + 1
    counters_path.write_text(json.dumps(counters, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return f"{prefix}{counters[prefix]:05d}"

def main():
    parser = argparse.ArgumentParser(description="Créer une fiche source dans le wiki")
    parser.add_argument("raw_pdf_path", help="Chemin vers le PDF")
    parser.add_argument("raw_txt_path", help="Chemin vers le TXT extrait")
    parser.add_argument("--title", default=None, help="Titre de la source (défaut : nom du PDF)")
    parser.add_argument("--theme", default="maintenance", choices=VALID_THEMES,
                        help="Thème cible (défaut : maintenance)")
    args = parser.parse_args()

    pdf_path = Path(args.raw_pdf_path)
    txt_path = Path(args.raw_txt_path)
    title = args.title or pdf_path.stem
    THEME_ROOT = WIKI_ROOT / "themes" / args.theme

    source_id = next_id("SRC")
    slug = slugify(title)
    theme = args.theme

    record_path = THEME_ROOT / "sources" / "records" / f"{source_id}-{slug}.md"
    today = datetime.date.today().isoformat()
    uid = str(uuid.uuid4())
    checksum = sha256_file(pdf_path) if pdf_path.exists() else ""

    rel_pdf = str(pdf_path).replace("\\", "/")
    rel_txt = str(txt_path).replace("\\", "/")
    rel_record = str(record_path).replace("\\", "/")

    text_status = "success" if txt_path.exists() and txt_path.stat().st_size > 0 else "failed"

    content = f"""---
uid: "{uid}"
id: "{source_id}"
type: "source_record"
status: "added"
created: "{today}"
updated: "{today}"

source:
  title: "{title}"
  author: ""
  organization: ""
  publication_date: ""
  source_type: "pdf"
  language: "fr"
  domain: []
  reliability: "unknown"
  confidence: "low"

files:
  raw_pdf: "{rel_pdf}"
  raw_txt: "{rel_txt}"
  original_filename: "{pdf_path.name}"
  checksum: "{checksum}"
  page_count: ""
  text_extraction_status: "{text_status}"

processing:
  added_by: "source_add"
  ingested: false
  ingestion_status: "not_started"
  last_ingested_at: ""
  ingestion_coverage: 0

generated_artifacts:
  atomic_notes: []
  glossary_terms: []
  norms: []
  normative_requirements: []
  business_processes: []
  domain_objects: []
  business_rules: []
  indicators: []
  mocs: []

logs:
  source_add_log: "data/generated/logs/wiki/{theme}/source-add/{source_id}-{slug}.md"
  ingestion_logs: []
---

# Source — {title}

## Résumé administratif

Document ajouté au wiki mais non encore analysé.

## Fichiers associés

- PDF original : `{rel_pdf}`
- Texte extrait : `{rel_txt}`

## État de traitement

- Conversion texte : {text_status}
- Ingestion : not_started
- Couverture : 0 %

## Artefacts générés depuis cette source

### Notes atomiques

Aucune pour l'instant.

### Glossaire

Aucun pour l'instant.

### Normes

Aucune pour l'instant.

### Exigences normatives

Aucune pour l'instant.

### Processus métier

Aucun pour l'instant.

### Objets métier

Aucun pour l'instant.

### Règles métier

Aucune pour l'instant.

### Indicateurs

Aucun pour l'instant.

### MOC

Aucun pour l'instant.

## Notes de traitement

-
"""

    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(content, encoding="utf-8")

    index_path = Path.cwd() / "data" / "generated" / "indexes" / args.theme / "sources.index.json"
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
    else:
        index = []

    index.append({
        "uid": uid,
        "id": source_id,
        "title": title,
        "path": rel_record,
        "raw_pdf": rel_pdf,
        "raw_txt": rel_txt,
        "status": "added",
        "ingestion_status": "not_started",
        "checksum": checksum
    })

    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    log_path = Path.cwd() / "data/generated/logs" / "wiki" / args.theme / "source-add" / f"{source_id}-{slug}.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(f"""# Log source_add — {source_id}

- Date : {today}
- Source : {title}
- PDF : {rel_pdf}
- TXT : {rel_txt}
- Record : {rel_record}
- Extraction texte : {text_status}
""", encoding="utf-8")

    print(rel_record)

if __name__ == "__main__":
    main()
