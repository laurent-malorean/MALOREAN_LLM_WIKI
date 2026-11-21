# /source_ingest

Utiliser le skill `.claude/skills/source-ingest/SKILL.md`.

Objectif :

- prendre une source TXT déjà enregistrée ;
- analyser le contenu progressivement par chunks ;
- créer ou mettre à jour les artefacts de connaissance ;
- maintenir les liens contextualisés ;
- mettre à jour les index JSON ;
- mettre à jour la fiche source ;
- créer un rapport d'ingestion.

Ne pas lire un gros fichier TXT en entier si cela risque de saturer le contexte.

Utiliser la stratégie de chunking décrite dans `.claude/rules/chunking-strategy.md`.

Les fusions doivent être proposées mais jamais exécutées automatiquement.
