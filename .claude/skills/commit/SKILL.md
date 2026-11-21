---
name: commit
metadata:
  project: parent
description: Commit dans les deux dépôts (app public + data privé) et met à jour data/generated/logs/commit.md
disable-model-invocation: true
---

# /commit

Le projet est réparti sur **deux dépôts git indépendants** :

- `app` : dépôt public (`MALOREAN_LLM_WIKI`), racine `.`. Contient `app/`, `.claude/`, `CLAUDE.md`, `README.md`, `pyproject.toml`, `uv.lock`.
- `data` : dépôt privé (`MALOREAN_LLM_WIKI_DATA`), racine `data/`. Contient `data/wiki/` et `data/generated/` (logs, état du site).

Le dépôt `app` ignore `data/`. Les commandes git du dépôt `data` s'écrivent `git -C data ...`.

## Arguments

- aucun : commit dans les deux dépôts (un dépôt sans changement est sauté) ;
- `app` : dépôt `app` seulement ;
- `data` : dépôt `data` seulement ;
- `all` : tout le working tree de chaque dépôt, en commits atomiques (voir plus bas) ;
- `push` : `git push` en fin de workflow, dans chaque dépôt commité.

Les arguments se combinent (`/commit data push`, `/commit all push`).

---

## Mode normal

> **PRIORITÉ ABSOLUE — commits atomiques.**
> Ne commiter que les fichiers produits par la **conversation courante**. Les fichiers modifiés hors conversation sont signalés mais exclus.
> `.gitignore` de chaque dépôt est la seule source de vérité pour l'exclusion.

Pour chaque dépôt visé :

1. Lancer `git status` et `git diff --name-only` (avec `-C data` pour `data`).
2. Identifier le périmètre : fichiers créés ou modifiés durant la conversation. En cas de doute sur l'origine d'un fichier, l'inclure.
3. S'il n'y a rien à commiter, passer au dépôt suivant.
4. **Ajouter** (append) une entrée à la fin de `data/generated/logs/commit.md` (fichier du dépôt `data`, privé, append-only) :
   ~~~
   ## YYYY-MM-DD HH:MM

   [app|data] type(scope): description courte

   Fichiers modifiés :
     - chemin/relatif/fichier

   Prompt: le prompt utilisateur qui a déclenché les modifications
   ~~~
5. Faire le `git commit` du dépôt avec les fichiers du périmètre.
6. Message : conventional commits (feat, fix, refactor, docs, chore), en français.

Ordre : commiter `app` d'abord, puis `data`. L'entrée du dépôt `app` est écrite dans `commit.md` avant le commit de `data`, pour qu'elle soit incluse dans celui-ci.

Ne jamais citer de prompt, de chemin de donnée ni de contenu du wiki dans un message de commit du dépôt `app` (public).

Fin : `git status` de chaque dépôt doit être propre, puis `git push` si `push` est passé (afficher le résultat complet).

---

## Mode `all`

> Commiter **tout le working tree** non ignoré de chaque dépôt visé.

1. `git status` du dépôt.
2. Grouper en commits atomiques par cohérence logique (préfixe de chemin, type de fichier, relation fonctionnelle), de 1 à ~10 fichiers par groupe quand c'est possible. Pour `data`, un commit par thème et par type d'opération est un bon découpage.
3. Pour chaque groupe : entrée dans `commit.md`, puis `git commit` avec uniquement les fichiers du groupe.
4. Vérifier `git status`. S'il reste des fichiers : commit final `chore: commit des fichiers restants`.
5. Récapitulatif : nombre de commits et fichiers par commit, par dépôt.
6. `git push` en fin de workflow si `push` est passé.

---

## Règles de sécurité

- Si `data/.git` n'existe pas, signaler que le dépôt `data` n'est pas initialisé et ne commiter que `app`.
- Ne jamais ajouter `data/` au dépôt `app`, ni de fichier du dépôt `app` au dépôt `data`.
- Avant un `push` du dépôt `app` (public), vérifier qu'aucun fichier suivi ne contient de chemin personnel ni de secret.
