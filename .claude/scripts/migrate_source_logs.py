#!/usr/bin/env python3
"""
Script de migration unique — met à jour les chemins logs dans les fiches sources.

Anciens formats :
  source_add_log: "wiki/{theme}/logs/source-add/..."
  source_add_log: "logs/source-add/..."
  source_add_log: "logs/{theme}/source-add/..."
  ingestion_logs: ["logs/ingestion/..."]
  ingestion_logs: ["wiki/{theme}/logs/ingestion/..."]
  ingestion_logs: ["logs/{theme}/ingestion/..."]

Nouveaux formats :
  source_add_log: "generated/logs/wiki/{theme}/source-add/..."
  ingestion_logs: ["generated/logs/wiki/{theme}/ingestion/..."]
"""

import re
from pathlib import Path

WIKI_ROOT = Path(__file__).parent.parent.parent / "wiki"
THEMES = [
    "maintenance", "product_management", "design_ux_ui", "ai_data_science",
    "marketing", "physique_quantique", "sociologie"
]


def migrate_file(path: Path, theme: str) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    # source_add_log: toutes variantes → "generated/logs/wiki/{theme}/source-add/..."
    text = re.sub(
        r'(source_add_log:\s*")wiki/' + re.escape(theme) + r'/logs/source-add/',
        r'\1_LOGS/wiki/' + theme + '/source-add/',
        text
    )
    text = re.sub(
        r'(source_add_log:\s*")logs/source-add/',
        r'\1_LOGS/wiki/' + theme + '/source-add/',
        text
    )
    text = re.sub(
        r'(source_add_log:\s*")logs/' + re.escape(theme) + r'/source-add/',
        r'\1_LOGS/wiki/' + theme + '/source-add/',
        text
    )

    # ingestion_logs: toutes variantes → "generated/logs/wiki/{theme}/ingestion/..."
    text = re.sub(
        r'"wiki/' + re.escape(theme) + r'/logs/ingestion/',
        '"generated/logs/wiki/' + theme + '/ingestion/',
        text
    )
    text = re.sub(
        r'"logs/ingestion/',
        '"generated/logs/wiki/' + theme + '/ingestion/',
        text
    )
    text = re.sub(
        r'"logs/' + re.escape(theme) + r'/ingestion/',
        '"generated/logs/wiki/' + theme + '/ingestion/',
        text
    )

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main():
    total = 0
    modified = 0

    for theme in THEMES:
        records_dir = WIKI_ROOT / "themes" / theme / "sources" / "records"
        if not records_dir.exists():
            continue
        for md_file in records_dir.glob("*.md"):
            total += 1
            if migrate_file(md_file, theme):
                modified += 1
                print(f"  [mise à jour] {md_file.relative_to(WIKI_ROOT.parent)}")

    print(f"\nTotal : {total} fiches, {modified} mises à jour.")


if __name__ == "__main__":
    main()
