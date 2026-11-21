# Règles — Texte réglementaire

> Les chemins ci-dessous sont relatifs à la racine du thème (`data/wiki/themes/{theme}/`).

## Définition

Un texte réglementaire documente une norme technique, une directive, une loi, un décret, un document réglementaire obligatoire ou un régime de classification qui s'impose à une organisation, un site ou une activité de maintenance.

Il répond à la question :

Quelle est l'obligation juridique ou normative, qui s'y applique, et ce qu'elle impose concrètement ?

## Emplacement

notes/regles-reglementaires/

## Préfixe

REG

## Sous-types

Un texte réglementaire doit avoir un `sub_type` parmi :

- `norme` — norme technique (NF, ISO, EN) non documentée en tant que fiche norme NOR
- `directive` — directive européenne (ex : Directive Seveso, Directive Machines)
- `loi_decret` — loi, décret, article du Code du travail, arrêté ministériel
- `document_reglementaire` — document exigé par la loi (Document Unique, EDD, POI, PPI)
- `classification` — régime de classification réglementaire (ICPE, ATEX, SEVESO seuil bas/haut)

## Différence avec NOR (fiche norme)

NOR est réservé aux normes techniques structurantes et complexes qui méritent une fiche complète avec exigences détaillées (NFX60-301, NF EN 13306).

REG couvre tous les autres textes réglementaires : directives, lois, décrets, classifications, documents obligatoires, et les normes moins développées citées en source.

Si une norme devient structurante pour le projet, envisager de la promouvoir en NOR.

## Format

---
uid: ""
id: "REG00000"
type: "regulatory_text"
sub_type: "directive"  # norme | directive | loi_decret | document_reglementaire | classification
status: "draft"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
title: ""
reference: ""           # code officiel ex: "2001/80/CE", "R. 4121-1 Code du travail"
issuer: ""              # "Union européenne", "État français", "AFNOR", "ISO"
publication_date: ""
geography: []           # ["France"], ["UE"], ["France", "UE"]
domain: []
source_ids: []
confidence: "medium"
---

# Titre du texte — référence officielle

## Objet

Décrire en 2 à 4 phrases ce que ce texte impose ou encadre.

## Périmètre d'application

- Géographie :
- Secteurs concernés :
- Installations ou activités visées :
- Seuils ou critères de déclenchement :

## Obligations principales

-

## Documents requis par ce texte

-

## Sanctions ou conséquences de non-conformité

-

## Liens contextualisés

- [[...]] — expliquer la relation.

## Sources

- Source :
- Localisation :
- URL brute :

## Questions ouvertes

-

## Notes qui pointent ici

-

## Règles

Créer un artefact REG si la source cite ou décrit un texte réglementaire, une directive, une loi, un décret, un document obligatoire ou un régime de classification qui s'impose à une organisation de maintenance.

Ne pas recopier massivement le texte réglementaire.

Si une obligation précise mérite un suivi, créer une fiche EXN (exigence normative) liée.

Si le terme réglementaire n'est pas encore dans le glossaire, créer une fiche GLO liée.

## Critères concrets d'inclusion

Créer un artefact REG si le texte :
- est cité nommément dans la source avec son code officiel ;
- impose des obligations à un exploitant, employeur ou prestataire ;
- classe un site, une installation ou une activité (ICPE, ATEX, Seveso) ;
- exige la production d'un document obligatoire (DU, EDD, POI, PPI) ;
- encadre des habilitations, certifications ou autorisations d'exercer.
