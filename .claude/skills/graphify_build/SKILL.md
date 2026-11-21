# Skill — graphify-build

## Déclenchement

```
/graphify_build [--theme <theme>]
```

Thèmes valides : voir `data/wiki/themes.json`. Défaut : `maintenance`.

## Mission

Construire le graphe de connaissances complet depuis les notes du wiki et stocker le résultat dans `data/generated/graphity/{theme}/graph.json`. C'est un rebuild complet — pour les mises à jour incrémentielles, utiliser `/graphify_update`.

## Important — pas de clé API

Le script local `.claude/skills/scripts/build_graph.py` parse les liens `[[ID-slug]]` Obsidian directement, sans LLM ni clé API. Ne jamais utiliser `graphify` (la commande `graphify`) pour la construction du graphe.

## Ce que Claude doit faire

1. Parser `--theme` (défaut : `maintenance`)
2. Vérifier que `data/wiki/themes/{theme}/notes/` existe
3. Construire le graphe via Bash :
   `uv run python .claude/skills/scripts/build_graph.py --theme {theme} --output data/generated/graphity/`
4. Générer le HTML via Bash :
   `uv run graphify cluster-only data/generated/graphity/{theme}/ --no-label --graph data/generated/graphity/{theme}/graph.json`
5. Afficher le résumé (nœuds, arêtes, communautés)
6. Confirmer les fichiers générés :
   - `data/generated/graphity/{theme}/graph.json` — graphe brut (pour path/explain/query)
   - `data/generated/graphity/{theme}/graphify-out/graph.html` — visualisation interactive
   - `data/generated/graphity/{theme}/graphify-out/GRAPH_REPORT.md` — rapport

## Ouvrir le graphe

```bash
open "data/generated/graphity/{theme}/graphify-out/graph.html"
```

## Après le build

Les commandes suivantes fonctionnent sur `data/generated/graphity/{theme}/graph.json` :
- `uv run graphify explain "ATO00001" --graph data/generated/graphity/{theme}/graph.json`
- `uv run graphify path "ATO00001" "GLO00050" --graph data/generated/graphity/{theme}/graph.json`

## Erreurs

- **`data/wiki/themes/{theme}/notes/` introuvable** : vérifier le nom du thème
- **`build_graph.py` introuvable** : le script est dans `.claude/skills/scripts/`
