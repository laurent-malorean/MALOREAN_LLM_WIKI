# Skill — source-ingest-batch

## Déclenchement

Utiliser ce skill quand l'utilisateur veut ingérer plusieurs sources en séquence sans intervention manuelle entre chacune.

Commande associée :

/source_ingest_batch

## Paramètre thème

Ce skill accepte un paramètre `theme` (défaut : `maintenance`).
Thèmes valides : voir `data/wiki/themes.json`.

## Paramètres

- Liste de sources : IDs séparés par espaces (`SRC00023 SRC00024 SRC00025`)
- `--theme {theme}` : thème cible (défaut : `maintenance`)

Exemple :

/source_ingest_batch SRC00023 SRC00024 --theme product_management

## Mission

Traiter chaque source de la liste séquentiellement en appliquant le pipeline complet de `source-ingest`, sans parallélisme.

Le traitement séquentiel est obligatoire — il garantit l'intégrité de `data/wiki/counters.json` et des index JSON. Ne jamais traiter deux sources simultanément.

## Pipeline

Pour chaque source dans la liste, dans l'ordre :

1. Résoudre la source :
   - Chercher `data/wiki/themes/{theme}/sources/records/` pour un fichier dont le nom commence par l'ID fourni.
   - Si la source n'existe pas, logger l'erreur et passer à la suivante.

2. Vérifier l'état d'ingestion :
   - Lire le frontmatter de la fiche source (`processing.ingested` et `processing.ingestion_status`).
   - Si `ingested: true` et `ingestion_coverage: 100`, logger "Source déjà ingérée — skip" et passer à la suivante.
   - Si `ingested: false` ou couverture incomplète, procéder.

3. Exécuter le pipeline complet de `source-ingest` pour cette source :
   - Appliquer intégralement les étapes 1 à 12 du SKILL.md de `source-ingest` (sans l'étape 13 fix-broken-slugs qui est exécutée une seule fois en fin de batch).
   - Ne pas abréger ni sauter d'étape.
   - Attendre la completion complète (rapport d'ingestion inclus) avant de passer à la source suivante.

4. Enregistrer le résultat dans le rapport de session (voir ci-dessous).

5. Passer à la source suivante.

Une fois toutes les sources traitées :

6. Corriger les slugs pour l'ensemble du wiki : `uv run python .claude/scripts/fix-broken-slugs.py`

## Rapport de session

Créer un rapport global dans :

data/generated/logs/wiki/{theme}/ingestion/batch-YYYY-MM-DD-HHmm/batch-report.md

Format :

```
# Rapport batch — YYYY-MM-DD HH:mm

## Thème
{theme}

## Sources traitées

| Source | Statut | ATO | GLO | Autres | Couverture |
|--------|--------|-----|-----|--------|------------|
| SRC00023 | complété | 22 | 18 | 1 MOC | 100% |
| SRC00024 | complété | 15 | 12 | 1 PRO | 95% |

## Sources ignorées

| Source | Raison |
|--------|--------|
| SRC00021 | déjà ingérée (ingestion_coverage: 100) |

## Erreurs

| Source | Erreur |
|--------|--------|

## Résumé

- Sources traitées : N
- Sources ignorées : N
- Erreurs : N
- Total artefacts créés : N
```

## Règles

Ne jamais traiter deux sources en parallèle.

Si une source échoue, continuer avec la suivante et noter l'erreur dans le rapport de session.

Ne pas modifier le comportement de `source-ingest` — ce skill est un orchestrateur, pas une réécriture.

Appliquer la passe terminologique finale et la passe réglementaire pour chaque source, comme défini dans `source-ingest/SKILL.md`.
