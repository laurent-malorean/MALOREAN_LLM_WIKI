# /wiki_api_start

Utiliser le skill `.claude/skills/wiki-api-start/SKILL.md`.

Objectif :

- Vérifier que l'API d'exploration du wiki n'est pas déjà lancée.
- Démarrer `app/api/wiki_api.py` en arrière-plan avec `uv run python`.
- Stocker le PID dans `tmp/wiki_api.pid`.
- Attendre le chargement des modèles en pollant `/health`.
- Confirmer que l'API répond sur http://localhost:8091.
