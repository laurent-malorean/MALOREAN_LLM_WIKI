# Règles — Liens contextualisés

## Principe

Un lien ne doit jamais être décoratif.

Chaque lien doit expliquer la relation.

Mauvais lien :

- [[Bon de travail]]

Bon lien :

- [[Bon de travail]] — une demande d'intervention peut être transformée en bon de travail après qualification.

## Types de relations

Utiliser des relations explicites :

- définit ;
- utilise ;
- clarifie ;
- contraste avec ;
- soutient ;
- nuance ;
- contredit ;
- illustre ;
- remplace ;
- remplacé par ;
- équivalent à ;
- proche de ;
- complète ;
- dépend de ;
- impacte ;
- nécessite ;
- produit ;
- alimente ;
- exemple de ;
- conséquence de ;
- cause de.

## Format des liens internes

Toujours utiliser le format complet `[[ID-slug]]`, jamais le seul identifiant `[[ID]]`.

Correct :

- `[[GLO00222-twi]]`
- `[[ATO00001-une-idee-principale]]`

Incorrect :

- `[[GLO00222]]`
- `[[ATO00001]]`

Le slug permet la résolution du lien dans Obsidian et dans le lint.

## Règle

Quand un lien est ajouté dans le corps d'un fichier, ajouter une courte explication textuelle.

## Backlinks

Les backlinks sont portés par la section `## Notes qui pointent ici` de chaque note, générée par `generate_backlinks.py`.

## Liens entre types

Exemples :

Norme vers glossaire :

- [[Disponibilité]] — terme défini ou stabilisé par cette norme.

Note atomique vers règle métier :

- [[REG00004-conserver-date-prevue-et-date-reelle]] — cette règle opérationnalise l'idée dans un workflow.

Processus vers objet métier :

- [[OBJ00002-demande-intervention]] — objet déclencheur du processus de qualification.
