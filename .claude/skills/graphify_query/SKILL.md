# Skill — graphify-query

## Déclenchement

```
/graphify_query [--theme <theme>] <question en langage libre>
```

Thèmes valides : voir `data/wiki/themes.json`. Défaut : `maintenance`.

## Mission

Interroger le graphe de connaissances existant (`data/generated/graphity/{theme}/graph.json`) avec une question en langage libre et retourner les nœuds et relations pertinents.

## Ce que Claude doit faire

1. Parser `--theme` (défaut : `maintenance`)
2. Résoudre le chemin du graphe : `data/generated/graphity/{theme}/graph.json`
3. Vérifier que ce fichier existe — sinon demander à l'utilisateur de lancer `/graphify_build --theme {theme}` d'abord
4. Exécuter via Bash :
   `uv run graphify query "<question>" --graph data/generated/graphity/{theme}/graph.json`
5. Afficher les résultats bruts
6. Synthétiser : nœuds trouvés, relations clés, artefacts wiki concernés (ID + titre)

## Exemple

```
/graphify_query quels concepts relient la maintenance préventive à la criticité ?
/graphify_query --theme marketing politique de marque et cohérence produit
```

## Erreurs

- **`data/generated/graphity/{theme}/graph.json` introuvable** : lancer `/graphify_build --theme {theme}` d'abord
