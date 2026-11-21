# Skill — db-rag-update

## Déclenchement

Utiliser ce skill quand l'utilisateur veut mettre à jour l'index RAG du wiki.

Commande associée :

/db_rag_update

## Paramètre thème

Ce skill accepte un paramètre `theme` (défaut : `maintenance`).
Thèmes valides : voir `data/wiki/themes.json`.

## Mission

Indexer ou ré-indexer toutes les notes du wiki dans la base vectorielle LanceDB pour un thème donné.

Détecte automatiquement les notes nouvelles, modifiées ou supprimées depuis la dernière indexation.
Produit un log dans `data/generated/logs/wiki/{theme}/rag/`.

## Pipeline

1. Vérifier que les dépendances Python sont installées avec uv (`uv sync`) :
   ```
   uv sync
   ```
   Si les dépendances sont déjà installées, passer directement à l'étape 2.

2. Lancer le script depuis la racine du projet avec `uv run` :
   ```
   uv run python app/rag/rag_update.py --theme {theme}
   ```

3. Lire le fichier de log généré dans `data/generated/logs/wiki/{theme}/rag/YYYY-MM-DD-rag-update.md`.

4. Résumer à l'utilisateur :
   - Thème traité
   - Nombre de notes ajoutées
   - Nombre de notes mises à jour
   - Nombre de notes supprimées
   - Total indexé
   - Durée
   - Chemin du log

## Sorties attendues

- `data/generated/rag/{theme}/index.lance/` — base vectorielle LanceDB mise à jour
- `data/generated/rag/{theme}/manifest.json` — manifest des fichiers indexés (chemin + mtime)
- `data/generated/logs/wiki/{theme}/rag/YYYY-MM-DD-rag-update.md` — log d'indexation

## Erreurs courantes

- **Dépendances manquantes** : lancer `uv sync`
- **Modèle non téléchargé** : `multilingual-e5-large` est téléchargé automatiquement au premier lancement
- **Dossier data/wiki/themes/{theme}/notes/ introuvable** : vérifier que le thème existe et que le script est lancé depuis la racine du projet

## Comportement incrémental

Le script ne ré-indexe que les notes dont le `mtime` a changé depuis la dernière exécution.
Un premier lancement indexe toutes les notes du thème.
Les lancements suivants sont rapides (seulement les modifications).
