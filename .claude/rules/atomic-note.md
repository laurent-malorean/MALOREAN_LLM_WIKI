# Règles — Note atomique

> Les chemins ci-dessous sont relatifs à la racine du thème (`data/wiki/themes/{theme}/`).

## Définition

Une note atomique contient une seule idée principale.

L'atomicité ne se mesure pas au nombre de mots. Elle se mesure à la cohésion interne : tout ce qu'il y a dans la note sert la même idée. Une note peut faire 3 lignes ou 20 lignes — si tout sert le même foyer conceptuel, elle reste atomique.

Elle n'est pas :

- une fiche de lecture ;
- un résumé ;
- une page thématique ;
- une collection d'idées ;
- une simple citation.

## Emplacement

notes/atomiques/

## Préfixe

ATO

## Critères

Une note atomique valide doit être :

- sourcée ;
- compréhensible seule ;
- réutilisable ;
- reliée à d'autres artefacts ;
- centrée sur une seule idée ;
- dotée d'un titre propositionnel.

## Test principal

Si retirer une partie de la note laisse une autre idée utile et autonome, la note doit être splittée.

Signaux de split supplémentaires :

- le titre est juste un mot vague (ex : "Maintenance", "Sécurité") ;
- la note contient plusieurs "mais", "cependant" qui ouvrent chacun une piste autonome ;
- la note juxtapose définition, exemple, objection et conclusion sans les distinguer ;
- la note est impossible à résumer en une phrase simple.

## Titre

Le titre doit exprimer une proposition.

Mauvais titre :

Maintenance préventive

Bon titre :

La maintenance préventive peut masquer des défauts structurels si les fréquences ne sont jamais révisées

## Anti-patterns de formulation

Ne jamais rédiger une note collée au contexte source. Reformuler en proposition autonome.

Mauvais :

Dans le chapitre 3, l'auteur explique que...

Bon :

La maintenance conditionnelle réduit les arrêts non planifiés quand les capteurs sont correctement calibrés

## Format

---
uid: ""
id: "ATO00000"
type: "atomic_note"
status: "draft"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
title: ""
aliases: []
confidence: "medium"
source_ids: []
tags: []
---

# Titre propositionnel

## Idée principale

Formuler l'idée centrale en 2 à 5 phrases.

## Pourquoi c'est important

Expliquer pourquoi cette idée est utile pour penser, décider, comparer ou concevoir.

## Origine / preuve

- Source :
- Localisation :
- URL brute :
- Niveau de confiance :

## Nuances et limites

Indiquer les conditions, exceptions ou incertitudes.

## Liens contextualisés

- [[...]] — expliquer la relation.

## Notes qui pointent ici

-

## Questions ouvertes

-

## Validation atomique

- Une seule idée principale :
- Titre propositionnel :
- Compréhensible hors source :
- Source traçable :
- Réutilisable :
- Liens contextualisés :
- Verdict :

## Règles

Créer une note atomique seulement si l'idée est distincte, sourcée et réutilisable.

Mettre à jour une note existante si la nouvelle source renforce, nuance, illustre ou contredit la même idée. Une note atomique est un point d'accrétion conceptuel : elle s'enrichit au fil de sources hétérogènes plutôt que d'être dupliquée par source.

Splitter automatiquement si une note contient clairement plusieurs idées indépendantes.

Ne jamais fusionner automatiquement.
