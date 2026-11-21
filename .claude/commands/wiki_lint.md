# /wiki_lint

Utiliser le skill `.claude/skills/wiki-lint/SKILL.md`.

Objectif :

- vérifier la cohérence du wiki ;
- détecter les fichiers sans identifiant ;
- détecter les liens cassés ;
- détecter les artefacts non indexés ;
- détecter les notes atomiques trop longues ou non atomiques ;
- détecter les sources non ingérées ;
- détecter les doublons probables ;
- produire un rapport dans `data/generated/logs/wiki/{theme}/lint/`.
