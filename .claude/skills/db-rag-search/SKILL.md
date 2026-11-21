# Skill — db-rag-search

## Déclenchement

Utiliser ce skill quand l'utilisateur veut rechercher dans les notes du wiki par similarité sémantique.

Commande associée :

/db_rag_search {all|type} {texte de requête}

## Paramètre thème

Ce skill accepte un paramètre `theme` (défaut : `maintenance`).
Thèmes valides : voir `data/wiki/themes.json`.

## Syntaxe

```
/db_rag_search all "maintenance prévisionnelle"
/db_rag_search ato "TPM opérateurs autonomes"
/db_rag_search glo "défaillance"
/db_rag_search pro "processus AMDEC"
```

## Types acceptés

| Argument | Type indexé |
|---|---|
| `all` | Tous les types |
| `ato` | atomic_note |
| `glo` | glossary_term |
| `nor` | norm_reference |
| `exn` | normative_requirement |
| `pro` | business_process |
| `obj` | domain_object |
| `brl` | business_rule |
| `reg` | regulatory_text |
| `hab` | habilitation |
| `ind` | indicator |
| `moc` | moc |

Les noms complets (`atomic_note`, `glossary_term`…) sont aussi acceptés directement.

## Mission

Effectuer une recherche sémantique dans la base RAG du thème et afficher les résultats sous forme de tableau compact.

## Pipeline

1. Parser la commande pour extraire :
   - `type_filter` : premier argument (`all` ou préfixe de type)
   - `query` : tout ce qui suit (la requête de recherche)

2. Vérifier que la base RAG existe (`data/generated/rag/{theme}/index.lance/`).
   Si elle n'existe pas, demander à l'utilisateur de lancer `/db_rag_update` d'abord.

3. Lancer :
   ```
   uv run python app/rag/rag_search.py --theme {theme} {type_filter} "{query}"
   ```

4. Afficher le tableau de résultats retourné par le script.

5. Si l'utilisateur demande à ouvrir une note, indiquer le chemin complet depuis la racine du projet.

## Sorties attendues

Tableau compact avec indication du thème dans l'en-tête.

## Erreurs courantes

- **Base introuvable** : lancer `/db_rag_update` pour créer l'index du thème
- **Type invalide** : utiliser les préfixes listés ci-dessus
- **Modèle non chargé** : le premier lancement télécharge `multilingual-e5-large`

## Options avancées

Pour augmenter le nombre de résultats (défaut : 10) :
```
uv run python app/rag/rag_search.py --theme {theme} all "requête" --top-k 20
```
