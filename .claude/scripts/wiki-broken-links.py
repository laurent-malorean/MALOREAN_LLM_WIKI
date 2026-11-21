#!/usr/bin/env python3
"""
Scan tous les liens cassés du wiki et persiste le rapport en mémoire.
Usage: uv run python .claude/scripts/scan-broken-links.py
"""
import re
import json
from pathlib import Path
from datetime import datetime

WIKI_ROOT = Path.cwd() / "data" / "wiki" / "themes"
MEMORY_FILE = WIKI_ROOT.parent.parent / "generated" / "logs" / "wiki" / "broken-links.json"

# Charger l'index des artefacts
artifacts_by_id = {}
for theme_dir in WIKI_ROOT.glob("*/"):
    theme = theme_dir.name
    if theme in ["counters.json", "memory"]:
        continue

    for search_dir in [theme_dir / "notes", theme_dir / "sources" / "records"]:
        if not search_dir.exists():
            continue
        for md_file in search_dir.rglob("*.md"):
            filename = md_file.name
            match = re.match(r'^([A-Z]{3}\d{5})-(.+)\.md$', filename)
            if match:
                artifact_id = match.group(1)
                artifacts_by_id[artifact_id] = True

print(f"📦 {len(artifacts_by_id)} artefacts trouvés")

# Scan des liens cassés
link_pattern = re.compile(r'\[\[([A-Z]{3}\d{5})(?:-[^\]]+)?\]\]')
broken_by_theme = {}
broken_links_set = set()

for md_file in WIKI_ROOT.rglob("*.md"):
    theme = md_file.parts[md_file.parts.index("wiki") + 1]

    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    for match in link_pattern.finditer(content):
        artifact_id = match.group(1)
        if artifact_id not in artifacts_by_id:
            broken_links_set.add(artifact_id)

            if theme not in broken_by_theme:
                broken_by_theme[theme] = {"links": set(), "files": []}

            broken_by_theme[theme]["links"].add(artifact_id)

            if md_file.relative_to(WIKI_ROOT) not in broken_by_theme[theme]["files"]:
                broken_by_theme[theme]["files"].append(str(md_file.relative_to(WIKI_ROOT)))

# Générer rapport
report = {
    "last_scan": datetime.utcnow().isoformat() + "Z",
    "summary": {
        "total_broken_links": len(broken_links_set),
        "themes_affected": len(broken_by_theme),
        "themes_clean": 8 - len(broken_by_theme)
    },
    "by_theme": {}
}

for theme in sorted(broken_by_theme.keys()):
    links = broken_by_theme[theme]["links"]
    report["by_theme"][theme] = {
        "broken_links_count": len(links),
        "broken_links": sorted(list(links)),
        "affected_files_count": len(broken_by_theme[theme]["files"]),
        "affected_files": sorted(broken_by_theme[theme]["files"])[:5]  # Top 5
    }

# Ajouter les thèmes propres
all_themes = set(d.name for d in WIKI_ROOT.glob("*/") if (d / "notes").exists())
for theme in sorted(all_themes - set(broken_by_theme.keys())):
    report["by_theme"][theme] = {"status": "clean"}

# Persister
MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(MEMORY_FILE, "w") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n✅ Rapport sauvegardé: {MEMORY_FILE.relative_to(WIKI_ROOT.parent.parent.parent)}")
print(f"\n📊 Résumé:")
print(f"  Liens cassés: {report['summary']['total_broken_links']}")
print(f"  Thèmes affectés: {report['summary']['themes_affected']}")
print(f"  Thèmes propres: {report['summary']['themes_clean']}")
