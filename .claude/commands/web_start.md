# /web_start

Utiliser le skill `.claude/skills/web-start/SKILL.md`.

Objectif :

- Vérifier que le serveur de révision n'est pas déjà lancé.
- Démarrer `app/website/server.py` en arrière-plan avec `uv run python`.
- Stocker le PID dans `tmp/website.pid`.
- Confirmer que le serveur répond sur http://localhost:8083.
