# Règles — Glossaire

> Les chemins ci-dessous sont relatifs à la racine du thème (`data/wiki/themes/{theme}/`).

## Définition

Une entrée de glossaire documente un terme du domaine.

Elle répond à la question :

Que signifie ce terme dans ce domaine ?

## Emplacement

notes/glossaire/

## Préfixe

GLO

## Format

---
uid: ""
id: "GLO00000"
type: "glossary_term"
status: "draft"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
term: ""
aliases: []
language: "fr"
english_equivalent: []
domain: []
confidence: "medium"
source_status: "sourced"
source_ids: []
---

# Terme

## Définition courte

Définition en 1 à 3 phrases.

## Définition détaillée

Expliquer le terme, son usage et son périmètre.

## Usage dans le domaine

Décrire comment le terme est utilisé concrètement.

## Synonymes et variantes

- Synonyme :
- Variante :
- Acronyme :
- Traduction anglaise :

## À ne pas confondre avec

- [[...]] — expliquer la différence.

## Liens contextualisés

- [[...]] — expliquer la relation.

## Exemples

-

## Ambiguïtés / débats

-

## Sources

- Source :
- URL brute :
- Localisation :

## Notes liées

-

## Notes qui pointent ici

-

## Passe terminologique finale

Après traitement de tous les chunks d'une source, effectuer une passe dédiée au glossaire.

Demander explicitement : quels termes importants du domaine ont été définis ou utilisés dans cette source et n'ont pas encore de fiche GLO dans le wiki ?

Créer les fiches manquantes si le terme est central, ambigu, récurrent ou structurant pour comprendre le domaine.

Ne pas se limiter aux termes créés "au fil" des chunks — certains termes peuvent avoir été absorbés dans d'autres artefacts sans jamais recevoir leur propre fiche.

## Règles

Créer une entrée de glossaire si le terme est central, ambigu, récurrent ou important pour comprendre le domaine.

Ne pas transformer une entrée de glossaire en article encyclopédique.

Si une entrée devient argumentative, extraire les idées dans des notes atomiques.

## Critères concrets d'inclusion

Créer une GLO si le terme :
- est une forme de maintenance (corrective, préventive, conditionnelle, prévisionnelle, améliorative...) ;
- est une opération de maintenance (dépannage, réparation, révision, inspection, visite...) ;
- est défini explicitement dans la source avec une phrase de définition ou une section dédiée ;
- apparaît dans le titre ou slug d'un artefact existant (ATO, PRO, IND, NOR) ;
- est normalisé (NF EN 13306, NF X60-110...).

## Complémentarité avec les autres types

La présence d'une ATO, PRO ou IND sur un concept ne dispense pas de créer une GLO.

- ATO = idée argumentée sur le concept
- PRO = enchaînement de tâches impliquant le concept
- IND = mesure quantifiable du concept
- GLO = définition stable du terme dans le domaine

Exemple : TPM existe en ATO00024 (transfert N1-N2) et IND00005 (TRS). Elle doit aussi avoir une GLO : définition de ce qu'est la TPM et de son périmètre.
