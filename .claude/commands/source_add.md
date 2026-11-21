# /source_add

Utiliser le skill `.claude/skills/source-add/SKILL.md`.

Objectif :

- prendre un PDF fourni par l'utilisateur ou présent dans le projet ;
- le copier dans `sources/raw/pdf/` ;
- extraire le texte dans `sources/raw/txt/` ;
- créer une fiche source Markdown dans `sources/records/` ;
- mettre à jour `data/wiki/counters.json` et `data/generated/indexes/{theme}/sources.index.json` ;
- créer un log dans `data/generated/logs/wiki/{theme}/source-add/`.

Ne pas analyser la source en profondeur.
Ne pas créer encore de notes atomiques, glossaire, normes ou autres artefacts métier.

Demander le chemin du PDF uniquement si aucun chemin n'est fourni.
