# Skill — wiki-broken-links

## Déclenchement

Utiliser ce skill pour scanner tous les liens cassés du wiki et générer un rapport en mémoire.

Commande associée :

`/wiki_broken_links`

## Mission

Identifier tous les liens `[[ID-slug]]` qui pointent vers une note inexistante ou supprimée.

Persister le rapport en JSON pour suivi futur.

## Exécution

Exécuter le script Python depuis la racine du projet :

```
uv run python .claude/scripts/wiki-broken-links.py
```

Ou utiliser la commande shell wrapper :

```
.claude/bin/wiki-broken-links
.claude/bin/wiki-broken-links --view
```

## Sortie

Le script génère un rapport JSON structuré dans `data/generated/logs/wiki/broken-links.json` avec :

- Nombre total de liens cassés
- Nombre de thèmes affectés / propres
- Détail par thème : liste des liens cassés, fichiers affectés
- Timestamp du dernier scan

### Exemple de sortie

```
📦 1861 artefacts trouvés

✅ Rapport sauvegardé: data/generated/logs/wiki/broken-links.json

📊 Résumé:
  Liens cassés: 17
  Thèmes affectés: 3
  Thèmes propres: 5
```

## Rapport JSON

```json
{
  "last_scan": "2026-05-30T13:22:54.363122Z",
  "summary": {
    "total_broken_links": 17,
    "themes_affected": 3,
    "themes_clean": 5
  },
  "by_theme": {
    "maintenance": {
      "broken_links_count": 14,
      "broken_links": ["GLO00028", "GLO00109", ...],
      "affected_files_count": 41,
      "affected_files": ["data/generated/logs/maintenance/lint/...", ...]
    },
    ...
    "design_ux_ui": { "status": "clean" }
  }
}
```

## Fréquence

- **Recommandée** : une fois par semaine
- **Critique** : après chaque ingestion massive de sources

## Résultat attendu

État sain : < 20 liens cassés avec la plupart en data/generated/logs/wiki/{theme}/lint/ (rapports historiques)

État critique : > 100 liens cassés (indique une dégradation structurelle)

## Notes

Les liens cassés se divisent en deux catégories :

1. **Orphelins temporaires** (logs de lint) — non critiques, nettoyage manuel
2. **Artefacts supprimés** — à décider si les références doivent être supprimées aussi

## Règle

Exécuter le scan régulièrement pour maintenir l'intégrité du wiki. Un rapport dégradé signale des fichiers supprimés sans mise à jour des références.
