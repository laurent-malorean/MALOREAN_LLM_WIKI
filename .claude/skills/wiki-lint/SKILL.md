# Skill — wiki-lint

## Déclenchement

Utiliser ce skill quand l'utilisateur veut vérifier la qualité du wiki.

Commande associée :

/wiki_lint

## Paramètre thème

Ce skill accepte un paramètre `theme` (défaut : `maintenance`).
Thèmes valides : voir `data/wiki/themes.json`.

## Mission

Analyser la cohérence du wiki pour un thème donné, sans créer de nouveaux artefacts métier.

## Contrôles

Vérifier :

- fichiers Markdown sans frontmatter ;
- artefacts sans `uid` ;
- artefacts sans `id` ;
- noms de fichiers incohérents ;
- fichiers non indexés ;
- entrées d'index pointant vers des fichiers absents ;
- liens Markdown cassés ;
- notes atomiques trop longues ;
- notes atomiques avec titre thématique ;
- glossaire sans définition courte ;
- norme sans code ou statut ;
- exigence normative sans norme source ;
- source sans TXT ;
- source non ingérée ;
- doublons probables ;
- liens non contextualisés.

## Sortie

Créer un rapport dans :

data/generated/logs/wiki/{theme}/lint/YYYY-MM-DD-lint-report.md

Ne pas modifier automatiquement les fichiers sauf demande explicite.
