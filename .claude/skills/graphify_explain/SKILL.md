# Skill — graphify-explain

## Déclenchement

```
/graphify_explain [--theme <theme>] <ID-slug>
```

Thèmes valides : voir `data/wiki/themes.json`. Défaut : `maintenance`.

## Mission

Expliquer un nœud du graphe : ses connexions, son rôle, ses voisins les plus proches.

## Ce que Claude doit faire

1. Parser `--theme` (défaut : `maintenance`)
2. Résoudre le chemin du graphe : `data/generated/graphity/{theme}/graph.json`
3. Vérifier que ce fichier existe — sinon demander à l'utilisateur de lancer `/graphify_build --theme {theme}` d'abord
4. Exécuter via Bash :
   `uv run graphify explain "<ID-slug>" --graph data/generated/graphity/{theme}/graph.json`
5. Afficher : type du nœud, degré entrant/sortant, top voisins les plus connectés, résumé contextuel

## Exemple

```
/graphify_explain GLO00050-tpm
/graphify_explain --theme marketing ATO00600-storybrand-hero
```

## Erreurs

- **`data/generated/graphity/{theme}/graph.json` introuvable** : lancer `/graphify_build --theme {theme}` d'abord
- **Nœud introuvable** : vérifier le slug exact (format `ID-slug-kebab-case`)
