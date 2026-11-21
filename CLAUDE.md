# CLAUDE.md — LDE_WIKI_IA

## Environnement Python

Ce projet est auto-porté. Il ne doit dépendre d'aucune librairie, outil ou configuration extérieure au projet.

### Utilisation obligatoire de uv

Toujours lancer Python via `uv` (environnement `.venv` géré par uv à la racine).

Ne jamais utiliser `python`, `pip`, `python3` ou `pip3` directement.

Commandes correctes :
```
uv run python <script>
uv sync
uv add <paquet>
```

Commandes interdites :
```
python <script>        # utilise l'interpréteur système ou Anaconda
pip install ...        # installe dans l'environnement global
```

### Dépendances

Toutes les dépendances du projet sont dans `pyproject.toml` à la racine (versions verrouillées dans `uv.lock`).

Ne jamais créer de `pyproject.toml` ni de `requirements.txt` dans un sous-dossier.

Pour ajouter une dépendance : `uv add <paquet>`.

### Indépendance du projet

Ce projet ne doit pas dépendre de :
- l'environnement Anaconda de la machine ;
- des packages installés globalement sur le système ;
- des fichiers ou configurations situés hors du répertoire du projet.

Tout ce qui est nécessaire au fonctionnement du projet doit être dans le projet.

## Structure du projet

```
.venv/                  environnement Python isolé (géré par uv)
pyproject.toml          toutes les dépendances (ingestion PDF + RAG)
uv.lock                 versions verrouillées
app/                    code (API, RAG, site de révision)
.claude/                skills, commandes, règles, hooks
tmp/                    fichiers temporaires
data/                   TOUTES les données (dépôt privé séparé, ignoré par ce dépôt)
  wiki/                 contenu du wiki, organisé par thème
    counters.json       compteurs globaux (partagés entre thèmes)
    memory/             mémoire persistante du projet
    themes/             maintenance, product_management, design_ux_ui,
                        ai_data_science, marketing, physique_quantique, sociologie
  generated/            généré (index, RAG, graphe, logs, mobile, état du site)
    indexes/            index générés (artifacts, sources), par thème
    rag/                base vectorielle LanceDB, par thème
    graphity/           graphe des liens, par thème
    logs/               logs et rapports
    mobileapp/          version mobile
    website/            état de révision du site
```

## Wiki

Le contenu du wiki est dans `data/wiki/`, organisé par thèmes. Voir `data/wiki/CLAUDE.md` pour la structure multi-thèmes et le CLAUDE.md de chaque thème pour les règles spécifiques au domaine.

## Thèmes

Les skills acceptent un paramètre `theme` (défaut : `maintenance`). Thèmes valides : `maintenance`, `product_management`, `design_ux_ui`, `ai_data_science`, `marketing`, `physique_quantique`.

## Liens wiki

Les liens internes doivent toujours utiliser le format `[[ID-slug]]` compatible Obsidian.

Ne jamais produire de liens en format Markdown `[texte](chemin)` pour les références internes au wiki.

Correct :
```
[[GLO00093-diagramme-de-gantt]]
```

Incorrect :
```
[Diagramme de Gantt](notes/glossaire/GLO00093-diagramme-de-gantt.md)
```

## Règles de comportement

Ne jamais ajouter spontanément du contenu non demandé (sections, résumés, reformulations, suggestions inline). Proposer explicitement si pertinent, mais ne jamais produire sans validation de l'utilisateur.

## Chemins dans les fichiers générés

Tous les fichiers générés par les skills (logs, rapports, index) doivent utiliser des **chemins relatifs** à la racine du projet.

Ne jamais écrire de chemin absolu dans un fichier versionné ou loggué.

Correct :
```
data/wiki/themes/maintenance/notes/atomiques/ATO00001-exemple.md
```

Incorrect :
```
/Users/x/projets/LDE_WIKI_IA/data/wiki/themes/maintenance/notes/atomiques/ATO00001-exemple.md
```

Cette règle s'applique à tous les fichiers produits : rapports lint, rapports d'ingestion, index, logs.

## Périmètre d'écriture

Il est **interdit** d'écrire des fichiers en dehors du répertoire du projet.

Tout fichier créé ou modifié par Claude doit être dans le répertoire racine du projet.

Ne jamais écrire dans `~/.claude/` ou tout autre chemin hors du projet.

La mémoire persistante du projet se trouve dans `data/wiki/memory/MEMORY.md` (versionné dans le dépôt de données).
