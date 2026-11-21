# Skill — source-add

## Déclenchement

Utiliser ce skill quand l'utilisateur veut ajouter une source PDF au wiki.

Commande associée :

/source_add

## Paramètre thème

Ce skill accepte un paramètre `theme` (défaut : `maintenance`).
Thèmes valides : voir `data/wiki/themes.json`.

Toutes les sorties sont créées sous `data/wiki/themes/{theme}/`.

## Mission

Ajouter une source PDF sans l'analyser en profondeur.

Le skill doit :

1. recevoir un chemin de PDF ;
2. recevoir un thème (défaut : maintenance) ;
3. vérifier que le fichier existe ;
4. générer un slug en kebab-case ;
5. générer un nouvel identifiant `SRCxxxxx` (compteurs globaux dans `data/wiki/counters.json`) ;
6. copier le PDF dans `data/wiki/themes/{theme}/sources/raw/pdf/` ;
7. extraire le texte dans `data/wiki/themes/{theme}/sources/raw/txt/` ;
8. créer une fiche source Markdown dans `data/wiki/themes/{theme}/sources/records/` ;
9. mettre à jour les index du thème (`data/generated/indexes/{theme}/`) ;
10. créer un log dans `data/generated/logs/wiki/{theme}/source-add/`.

## Règles à lire

Avant d'agir, lire :

- `.claude/rules/id-conventions.md`
- `.claude/rules/source-file.md`

## Sorties attendues

Pour un PDF nommé :

Guide Maintenance Préventive.pdf

Créer :

data/wiki/themes/{theme}/sources/raw/pdf/SRC00001-guide-maintenance-preventive.pdf
data/wiki/themes/{theme}/sources/raw/txt/SRC00001-guide-maintenance-preventive.txt
data/wiki/themes/{theme}/sources/records/SRC00001-guide-maintenance-preventive.md
data/generated/logs/wiki/{theme}/source-add/SRC00001-guide-maintenance-preventive.md

## Comportement

Ne pas créer d'artefacts de connaissance à ce stade.

La fiche source doit rester minimale.

Elle doit contenir les chemins vers le PDF et le TXT.

Elle doit contenir des listes vides pour les artefacts générés.

## Erreurs

Si l'extraction texte échoue, créer quand même la fiche source avec :

text_extraction_status: failed

et documenter l'erreur dans le log.
