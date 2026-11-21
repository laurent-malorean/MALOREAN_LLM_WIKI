# Règles — Chunking des sources longues


## Objectif

Traiter des sources TXT longues sans saturer le contexte et sans perdre les idées à cheval entre deux sections.

## Stratégie

Ne pas couper arbitrairement toutes les 100 lignes.

Utiliser une stratégie en plusieurs niveaux :

1. pré-segmentation structurelle ;
2. regroupement en chunks de taille contrôlée ;
3. overlap léger ;
4. manifest de suivi ;
5. déduplication via index.

## Marqueurs structurels

Privilégier les coupures :

- avant un titre ;
- avant une nouvelle section ;
- après un paragraphe complet ;
- après une liste complète ;
- après une page si c'est cohérent.

Éviter les coupures :

- au milieu d'un paragraphe ;
- entre un titre et son contenu ;
- au milieu d'une liste ;
- au milieu d'un tableau ;
- au milieu d'une idée.

## Taille

Taille cible :

2 000 à 4 000 mots

Taille maximale :

6 000 mots

Si le manifest contient un chunk dépassant 6 000 mots, il DOIT être redécoupé avant traitement. Ne jamais traiter un chunk de plus de 6 000 mots en une seule passe.

## Overlap

Ajouter un overlap de 2 à 5 paragraphes.

L'overlap doit être marqué comme contexte.

Ne pas créer une note uniquement depuis l'overlap.

## Manifest

Créer un fichier :

data/generated/logs/wiki/{theme}/ingestion/SRCxxxxx-slug/chunks.json

Chaque chunk doit avoir :

- chunk_id ;
- start_page ;
- end_page ;
- start_char ;
- end_char ;
- status ;
- artifacts_created ;
- artifacts_updated ;
- notes.

## Périmètre "référence technique"

Le classement "référence technique" (sans extraction d'artefacts) est réservé aux contenus qui ne passent pas le test atomique :

> **Test : ce contenu contient-il une idée exprimable en une proposition, compréhensible hors source, réutilisable dans un autre contexte ?**

Si oui → extraire une ATO, même si le chapitre est à dominante technique ou méthodologique.

Si non → classer "référence technique" et documenter pourquoi dans le champ `note` du chunk.

Ce classement strict s'applique uniquement à :
- données purement numériques sans principe derrière (tableaux de tolérances, nomenclatures de pièces, listes de références) ;
- procédures step-by-step sans idée générale extractable ("étape 1 : ouvrir le capot, étape 2 : vérifier le niveau") ;
- index, bibliographies, notes de bas de page.

Ne jamais classer "référence technique" un chunk au motif qu'il est :
- méthodologique (une méthode a toujours un principe derrière) ;
- technique (les techniques ont des logiques réutilisables) ;
- complémentaire à une ATO existante (une idée complémentaire distincte mérite sa propre ATO) ;
- déjà partiellement couvert par une autre source (l'angle spécifique de la source actuelle peut être distinct).

## Règle

Avant chaque chunk, charger les index courts.

Ne charger les fichiers Markdown complets que si l'index indique une proximité forte.
