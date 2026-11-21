# Skill — graphify-update

## Déclenchement

```
/graphify_update [--theme <theme>]
```

Thèmes valides : voir `data/wiki/themes.json`. Défaut : `maintenance`.

## Mission

Mettre à jour le graphe de connaissances existant après une ingestion. Relance le script local (rebuild complet — il est rapide, ~5s pour 1000 notes).

À utiliser après chaque `/source_ingest`.

## Important — pas de clé API

Le script `.claude/skills/scripts/build_graph.py` parse les liens `[[ID-slug]]` Obsidian directement, sans LLM ni clé API.

## Ce que Claude doit faire

1. Parser `--theme` (défaut : `maintenance`)
2. Vérifier que `data/generated/graphity/{theme}/graph.json` existe — sinon dire à l'utilisateur de lancer `/graphify_build --theme {theme}` d'abord
3. Vérifier que `data/wiki/themes/{theme}/notes/` existe
4. Reconstruire le graphe via Bash :
   `uv run python .claude/skills/scripts/build_graph.py --theme {theme} --output data/generated/graphity/`
5. Régénérer le HTML via Bash :
   `uv run graphify cluster-only data/generated/graphity/{theme}/ --no-label --graph data/generated/graphity/{theme}/graph.json`
6. Afficher le résumé : nœuds, arêtes, communautés
7. Confirmer les fichiers mis à jour :
   - `data/generated/graphity/{theme}/graph.json`
   - `data/generated/graphity/{theme}/graphify-out/graph.html`

## Quand utiliser build vs update

| Situation | Commande |
|---|---|
| Premier lancement | `/graphify_build` |
| Après une ingestion (`/source_ingest`) | `/graphify_update` |
| Après ajout d'un nouveau thème | `/graphify_build --theme {nouveau_theme}` |
| Graphe incohérent ou corrompu | `/graphify_build` (rebuild complet) |

## Erreurs

- **`data/generated/graphity/{theme}/graph.json` introuvable** : lancer `/graphify_build --theme {theme}` d'abord
- **`data/wiki/themes/{theme}/notes/` introuvable** : vérifier le nom du thème
