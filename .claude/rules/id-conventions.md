# Règles — Identifiants et noms de fichiers

## Double identifiant

Chaque artefact doit avoir :

uid: UUID technique stable
id: identifiant humain croissant

Exemple :

uid: "550e8400-e29b-41d4-a716-446655440000"
id: "ATO00001"

## Préfixes

SRC : source
ATO : note atomique
GLO : glossaire
NOR : norme
EXN : exigence normative
PRO : processus métier
OBJ : objet métier
BRL : règle métier (Business RuLe)
REG : texte réglementaire (directive, loi, décret, classification, document obligatoire)
HAB : habilitation
IND : indicateur
MOC : carte de navigation

## Format de l'identifiant humain

Préfixe 3 lettres + numéro croissant sur 5 chiffres.

Exemples :

SRC00001
ATO00001
GLO00001
NOR00001

## Nom de fichier

Le nom de fichier doit suivre ce format :

ID-slug-kebab-case.md

Exemple :

ATO00001-une-demande-intervention-mal-qualifiee-degrade-la-planification.md

## Slug

Le slug doit être :

- en minuscules ;
- sans accents ;
- en kebab-case ;
- sans ponctuation inutile ;
- suffisamment descriptif ;
- pas trop long.

## Compteurs

Les compteurs sont **globaux** (partagés entre tous les thèmes) et stockés dans :

data/wiki/counters.json

Quand un artefact est créé :

1. lire `data/wiki/counters.json` ;
2. incrémenter le compteur du préfixe ;
3. générer l'identifiant ;
4. sauvegarder `data/wiki/counters.json`.

## Règle

Ne jamais réutiliser un identifiant.

Même si un fichier est archivé ou supprimé, son identifiant ne doit pas être repris.
