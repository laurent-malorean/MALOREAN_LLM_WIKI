# Règles — Habilitation

> Les chemins ci-dessous sont relatifs à la racine du thème (`data/wiki/themes/{theme}/`).

## Définition

Une habilitation documente une autorisation formelle, une certification ou un permis obligatoire requis pour réaliser une activité spécifique de maintenance présentant des risques particuliers.

Elle répond à la question :

Quelle qualification formelle est requise pour réaliser cette activité, qui la délivre, et quelles sont les conditions de validité ?

## Emplacement

notes/habilitations/

## Préfixe

HAB

## Format

---
uid: ""
id: "HAB00000"
type: "habilitation"
status: "draft"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
name: ""
aliases: []
domain: []
source_ids: []
confidence: "medium"

habilitation:
  type: ""              # permis_feu | habilitation_electrique | travail_hauteur | espace_confine | atex | radioprotection | autre
  regulatory_basis: ""  # texte réglementaire de référence
  issuer: ""            # employeur | organisme_certif | prefecture | autre
  validity_duration: "" # ex: "3 ans", "sans limite avec recyclage annuel"
  renewable: true
---

# Nom de l'habilitation

## Définition courte

-

## Activités concernées

Décrire les opérations de maintenance qui requièrent cette habilitation.

## Conditions d'obtention

-

## Durée et renouvellement

-

## Qui délivre

-

## Obligations de l'employeur

-

## Risques en cas d'absence d'habilitation

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

Créer un artefact HAB si la source mentionne une habilitation, certification, permis ou autorisation formelle requise pour réaliser une activité de maintenance.

Ne pas confondre habilitation (autorisation individuelle d'exercer) et classification réglementaire (régime applicable à un site ou équipement — → REG).

## Critères concrets d'inclusion

Créer un artefact HAB si :
- la source cite nommément un permis, une habilitation ou une certification (permis de feu, habilitation électrique, travail en hauteur, espace confiné, ATEX, radioprotection) ;
- la source précise que certaines activités ne peuvent être réalisées que par des personnels habilités ou certifiés ;
- la source décrit les conditions d'obtention, de renouvellement ou de retrait d'une habilitation.
