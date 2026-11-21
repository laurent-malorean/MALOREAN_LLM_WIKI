# Skill — wiki-search

## Déclenchement

Utiliser ce skill quand l'utilisateur exprime un besoin en langage libre et veut retrouver les notes existantes du wiki qui y répondent.

Commande associée :

/wiki-search {besoin exprimé librement}

## Paramètre thème

Ce skill accepte un paramètre `--theme` (défaut : `maintenance`).
Thèmes valides : voir `data/wiki/themes.json`.

## Paramètre --json

Ce skill accepte un paramètre facultatif `--json`.

Si présent, produire **uniquement** la sortie JSON (pas de tableaux Markdown, pas de note explicative en prose).

Format de sortie :

```json
{
  "query": {
    "theme": "marketing",
    "raw": "Positionnement produit SaaS B2B",
    "queries_used": [
      "positionnement produit B2B SaaS marché",
      "segmentation différenciation proposition de valeur acheteur B2B concurrence"
    ]
  },
  "results": [
    {
      "id": "GLO00441",
      "type": "glossary_term",
      "title": "positionnement produit",
      "path": "data/wiki/themes/marketing/notes/glossaire/GLO00441-positionnement-produit.md",
      "rag_score": 4.197,
      "graph_degree": 12,
      "sources": ["rag", "graph"],
      "relevance": 5,
      "category": "glossaire"
    }
  ],
  "coverage_gaps": [
    "Pas de notes spécifiques au positionnement SaaS (pricing, freemium, ICP logiciels B2B)"
  ],
  "total_raw": 18,
  "total_deduplicated": 13
}
```

**Champs :**
- `query.raw` — texte brut saisi par l'utilisateur
- `query.queries_used` — les 2 requêtes RAG construites
- `results[].rag_score` — score brut retourné par le modèle (float, peut être négatif, `null` si absent du RAG)
- `results[].graph_degree` — degré du nœud dans le graphe (`null` si absent du graphe)
- `results[].sources` — origines : `"rag"` | `"graph"` | `["rag", "graph"]`
- `results[].relevance` — 1 à 5, évaluation sémantique post-fusion
- `results[].category` — `glossaire` | `atomique` | `navigation`
- `coverage_gaps` — zones du besoin non couvertes par le wiki
- `total_raw` — nombre de résultats bruts avant déduplication
- `total_deduplicated` — nombre de résultats après déduplication

## Syntaxe

```
/wiki-search comment bien positionner un produit sur son marché
/wiki-search --theme marketing je veux comprendre la fidélisation client
/wiki-search --theme product_management priorisation du backlog face à l'incertitude
/wiki-search --theme marketing --json positionnement produit SaaS B2B
```

## Mission

À partir d'un besoin exprimé librement, combiner une recherche sémantique RAG et une traversée du graphe de connaissances, puis synthétiser les résultats des deux sources pour produire la réponse la plus complète et la mieux contextualisée possible.

## Pipeline

### 1. Analyse du besoin

Identifier :
- Le **concept central** exprimé par l'utilisateur
- Les **concepts sous-jacents** : synonymes, composantes, angles connexes, tensions structurantes, opposés pertinents
- Les **2 à 3 termes pivots** les plus susceptibles d'être des ID de nœuds dans le graphe (ex : `GLO00050-tpm`, `ATO00024-...`)

Ne pas interroger le RAG directement avec la phrase brute de l'utilisateur.
Reformuler en requêtes sémantiquement riches.

### 2. Recherche RAG (branche A)

Construire **2 requêtes complémentaires** :
- Requête 1 : concept central (termes directs, termes du domaine)
- Requête 2 : concepts sous-jacents regroupés en une phrase dense

Lancer **en parallèle** (deux appels Bash simultanés) :
```
uv run python app/rag/rag_search.py --theme {theme} all "{requête1}" --top-k 15
uv run python app/rag/rag_search.py --theme {theme} all "{requête2}" --top-k 15
```

Collecter les résultats : ID, type, titre, score RAG.

### 3. Traversée graphe (branche B)

Vérifier que `data/generated/graphity/{theme}/graph.json` existe. Si absent, sauter cette étape et le signaler (suggérer `/graphify_build --theme {theme}`).

Construire une requête graphe à partir des termes pivots identifiés à l'étape 1 :
```
uv run graphify query "{termes pivots}" --graph data/generated/graphity/{theme}/graph.json
```

Collecter les résultats : ID-slug, type, fichier source.

### 4. Fusion et déduplication

- Agréger les résultats RAG (branche A) et graphe (branche B) dans une liste unique
- Dédupliquer par ID : si un artefact apparaît dans les deux sources, conserver une seule entrée avec `"sources": ["rag", "graph"]`
- Annoter chaque entrée avec son origine (`rag` seul, `graph` seul, ou les deux)
- Les artefacts présents dans les **deux sources** sont les plus fiables : ils sont sémantiquement proches ET structurellement connectés

### 5. Évaluation et classement

Pour chaque artefact dédupliqué, évaluer sa pertinence (1 à 5) par rapport au besoin exprimé selon ces critères combinés :

| Critère | Poids |
|---|---|
| Présence dans les deux sources (RAG + graphe) | Bonus fort |
| Score RAG élevé (> 0) | Positif |
| Nœud à fort degré dans le graphe | Indicateur de centralité |
| Proximité sémantique avec le concept central | Déterminant |

Écarter les artefacts dont le lien est trop faible ou indirect (score RAG très négatif ET absent du graphe).

### 6. Réponse structurée

**Sans `--json`** : produire trois tableaux Markdown séparés :

**Glossaire** — termes structurants du domaine liés au besoin
**Notes atomiques** — idées clés directement pertinentes
**Navigation & processus** — MOC, PRO, IND si présents et pertinents

Chaque entrée comporte :
- L'ID cliquable (lien relatif Markdown depuis la racine du projet)
- Le titre complet de la note
- La source : `[RAG]`, `[Graphe]` ou `[RAG+Graphe]`
- Un degré de confiance de 1 à 5 ⭐ basé sur la fusion des deux signaux

**Avec `--json`** : produire uniquement le bloc JSON défini dans la section "Paramètre --json". Pas de tableaux, pas de prose.

### 7. Note explicative

Sans `--json`, conclure par :
- Une phrase expliquant ce que le RAG a trouvé que le graphe n'aurait pas remonté (et vice-versa)
- Un signal si des zones du besoin ne sont pas couvertes par le wiki

## Barème du degré de confiance

| Score | Signification |
|-------|---------------|
| ⭐⭐⭐⭐⭐ | Présent dans RAG + graphe, concept central traité explicitement |
| ⭐⭐⭐⭐ | Présent dans une seule source mais fortement pertinent |
| ⭐⭐⭐ | Lié — concept connexe utile pour contextualiser |
| ⭐⭐ | Adjacents — concept périphérique, à mobiliser avec précaution |
| ⭐ | Faiblement lié — ne retenir que si le wiki est peu couvert sur le sujet |

## Erreurs courantes

- **Base RAG introuvable** : lancer `/db_rag_update --theme {theme}` d'abord
- **`data/generated/graphity/{theme}/graph.json` introuvable** : lancer `/graphify_build --theme {theme}` d'abord — le skill fonctionne en mode RAG seul si le graphe est absent
- **Requête trop courte** : enrichir avec les concepts sous-jacents avant d'interroger
- **Modèle non chargé** : le premier lancement télécharge `multilingual-e5-large`
