#!/bin/bash
# PreToolUse (Bash) — avertit quand rag_search.py est appelé seul, hors du
# pipeline /wiki-search (qui combine RAG + traversée de graphe).
#
# But : rappeler qu'une recherche de contenu dans le wiki doit passer par
# /wiki-search (RAG + graphe + fusion/classement), plus complet que le RAG seul.
#
# Non bloquant : on émet un rappel sur stderr avec exit 2 (le message remonte à
# l'agent comme feedback), mais on ne refuse pas l'exécution — les usages
# légitimes de rag_search.py restent possibles.

if ! command -v jq &>/dev/null; then exit 0; fi

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Rien à faire si la commande n'appelle pas rag_search.py
case "$CMD" in
  *rag_search.py*) ;;
  *) exit 0 ;;
esac

# Échappatoires — appels légitimes, on reste silencieux :
# 1) le pipeline complet est lancé (RAG + graphe dans la même commande) ;
# 2) marqueur explicite --solo-rag ajouté volontairement par l'utilisateur.
case "$CMD" in
  *graphify*|*--solo-rag*) exit 0 ;;
esac

# Sinon : rappel non bloquant.
echo "RAPPEL : rag_search.py est appelé seul. Pour retrouver du contenu du wiki, préférer /wiki-search (RAG + graphe + fusion), plus complet que le RAG seul. Si l'appel RAG isolé est volontaire (debug, db-rag-update), ajouter --solo-rag à la commande pour supprimer ce rappel." >&2
exit 2
