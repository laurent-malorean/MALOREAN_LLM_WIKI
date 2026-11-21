# /wiki_gap

Utiliser le skill `.claude/skills/wiki-gap/SKILL.md`.

Objectif :

- détecter les artefacts manquants dans toutes les sources ingérées ;
- identifier les termes sans fiche GLO, idées sans fiche ATO, indicateurs sans fiche IND, processus sans fiche PRO, règles sans fiche REG ;
- proposer une liste à l'utilisateur pour validation ;
- créer les fiches sélectionnées en respectant toutes les règles du wiki ;
- produire un rapport dans `data/generated/logs/wiki/{theme}/gap-analysis/`.
