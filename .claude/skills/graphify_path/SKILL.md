# Skill — graphify-path

## Déclenchement

```
/graphify_path [--theme <theme>] <ID-slug-A> <ID-slug-B>
```

Thèmes valides : voir `data/wiki/themes.json`. Défaut : `maintenance`.

## Mission

Trouver le chemin relationnel entre deux artefacts du wiki dans le graphe de connaissances.

## Ce que Claude doit faire

1. Parser `--theme` (défaut : `maintenance`)
2. Résoudre le chemin du graphe : `data/generated/graphity/{theme}/graph.json`
3. Vérifier que ce fichier existe — sinon demander à l'utilisateur de lancer `/graphify_build --theme {theme}` d'abord
4. Exécuter via Bash :
   `uv run graphify path "<ID-slug-A>" "<ID-slug-B>" --graph data/generated/graphity/{theme}/graph.json`
5. Afficher le chemin : liste ordonnée des nœuds intermédiaires avec les types de relations entre chaque étape

## Exemple

```
/graphify_path ATO00017-zone-optimale-entre-preventif-et-correctif GLO00050-tpm
/graphify_path --theme marketing ATO00600-storybrand-hero GLO00441-positionnement-produit
```

## Erreurs

- **`data/generated/graphity/{theme}/graph.json` introuvable** : lancer `/graphify_build --theme {theme}` d'abord
- **Nœud introuvable** : vérifier le slug exact (format `ID-slug-kebab-case`)
