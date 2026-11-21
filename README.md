# LDE_WIKI_IA

Wiki personnel multi-thèmes, alimenté par l'ingestion de PDF et piloté avec Claude Code.

Le principe : on ajoute un PDF, on en extrait le texte, puis on le découpe en notes liées entre elles (notes atomiques, glossaire, normes, processus, indicateurs…). Le tout est consultable dans Obsidian, par recherche sémantique (RAG), par graphe, et via un site web de révision.

Thèmes : `maintenance`, `product_management`, `design_ux_ui`, `ai_data_science`, `marketing`, `physique_quantique`, `sociologie`.

## En savoir plus sur le LLM wiki

Pour comprendre l'idée, la démarche et les usages d'un wiki alimenté par un LLM, lisez la présentation [Conf001-Wiki-IA.pdf](Conf001-Wiki-IA.pdf) à la racine du dépôt.

## Structure

```
app/          code de l'application (API, RAG, site de révision)
data/         toutes les données (dépôt privé séparé)
  wiki/       contenu du wiki (notes, sources, compteurs, mémoire)
  generated/  généré (index, RAG, graphe, logs, mobile, état du site)
tmp/          fichiers temporaires
.claude/      skills, commandes, règles et hooks Claude Code
.obsidian/    configuration Obsidian
.venv/        environnement Python (géré par uv)
```

Ce dépôt contient le moteur. Les données vivent dans `data/`, qui est un dépôt privé distinct (`MALOREAN_LLM_WIKI_DATA`) ignoré par celui-ci.

## Où sont les données

- `data/wiki/themes/{theme}/notes/` : notes du wiki, par type.
- `data/wiki/themes/{theme}/sources/` : PDF originaux, textes extraits, fiches sources.
- `data/wiki/counters.json` : compteurs d'identifiants (ne jamais réutiliser un ID).
- `data/wiki/memory/` : mémoire persistante du projet.
- `data/generated/indexes/{theme}/` : index des artefacts et des sources.
- `data/generated/rag/{theme}/` : base vectorielle LanceDB.
- `data/generated/graphity/{theme}/` : graphe des liens entre notes.
- `data/generated/logs/` : logs et rapports (ingestion, lint, liens cassés, RAG).
- `data/generated/mobileapp/` : version mobile générée.
- `data/generated/website/` : état de révision du site.

`data/generated/` se régénère à partir de `data/wiki/`, sauf `logs/` et `website/` (traçabilité et état de révision).

## Démarrer avec un wiki vide

`template/data/` contient le squelette de `data/` (thèmes, compteurs à zéro, dossiers vides).

```
cp -r template/data data
```

Pour utiliser un dépôt de données existant, le cloner dans `data/`.

## Installation

Le projet utilise [uv](https://docs.astral.sh/uv/). Les dépendances sont dans `pyproject.toml`.

```
uv sync
```

Toujours lancer Python avec `uv run python <script>`. Ne jamais utiliser `python` ou `pip` directement.

Outils système requis (non installés par uv), sur Mac avec Homebrew :

```
brew install poppler tesseract ghostscript
```

`poppler` fournit `pdftotext` (extraction du texte des PDF). `tesseract` et `ghostscript` servent à l'OCR des PDF scannés.

## Utilisation

Les actions se lancent avec des skills Claude Code (dossier `.claude/skills/`) :

- `/source_add` : ajouter un PDF au wiki.
- `/source_ingest` : extraire les notes d'une source.
- `/wiki_lint` : vérifier le wiki.
- `/wiki_gap` : repérer ce qui manque après une ingestion.
- `/wiki-search` : rechercher dans le wiki (RAG + graphe).
- `/web_start` et `/web_stop` : site de révision (port 8083).
- `/wiki_api_start` et `/wiki_api_stop` : API d'exploration (port 8091).
- `/mobileapp_build` : générer la version mobile.

## Conventions

- Liens internes au format Obsidian `[[ID-slug]]`.
- Chemins toujours relatifs à la racine du projet.
- Détails et règles : `CLAUDE.md`, `data/wiki/CLAUDE.md` et `.claude/rules/`.
