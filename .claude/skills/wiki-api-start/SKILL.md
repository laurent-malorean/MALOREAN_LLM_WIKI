# Skill — wiki-api-start

## Déclenchement

Utiliser ce skill quand l'utilisateur veut démarrer l'API d'exploration du wiki.

Commande associée :

/wiki_api_start

## Mission

1. Vérifier si l'API est déjà lancée (lire `tmp/wiki_api.pid` si existant, tester avec `kill -0 $PID`).
2. Si déjà lancée, informer l'utilisateur et ne rien faire.
3. Lancer `app/api/wiki_api.py` en arrière-plan avec `uv run` du projet.
4. Stocker le PID dans `tmp/wiki_api.pid`.
5. Rediriger les logs vers `tmp/wiki_api.log`.
6. Attendre le chargement des modèles (embedding + re-ranker, ~15-20 s) en **pollant** `/health`.
7. Confirmer que l'API répond sur `http://localhost:8091`.

## Chemins

- Interpréteur : `uv run python`
- Script : `app/api/wiki_api.py`
- PID : `tmp/wiki_api.pid`
- Log : `tmp/wiki_api.log`
- Port : `8091`

## Note importante

Contrairement au serveur de révision (`/web_start`), l'API charge deux modèles
lourds au démarrage (`multilingual-e5-large` + cross-encoder). Le boot prend
**~15-20 secondes**. Ne pas se contenter d'un `sleep 2` : poller `/health`
jusqu'à ce qu'il réponde `200`.

## Commandes à exécuter

```bash
PID_FILE="$(pwd)/tmp/wiki_api.pid"
LOG_FILE="$(pwd)/tmp/wiki_api.log"
PORT=8091

# Vérifier si déjà lancé
if [ -f "$PID_FILE" ]; then
  EXISTING_PID=$(cat "$PID_FILE")
  if kill -0 "$EXISTING_PID" 2>/dev/null; then
    echo "API déjà lancée (PID $EXISTING_PID) — http://localhost:$PORT"
    exit 0
  fi
fi

# Lancer l'API
uv run python \
  "app/api/wiki_api.py" --port "$PORT" \
  >> "$LOG_FILE" \
  2>&1 &

echo $! > "$PID_FILE"
echo "API en cours de démarrage (PID $(cat $PID_FILE)) — chargement des modèles..."

# Attendre le chargement des modèles (poll /health, max ~40 s)
UP=0
for i in $(seq 1 20); do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/health" 2>/dev/null)
  if [ "$HTTP_CODE" = "200" ]; then
    UP=1
    echo "API OK après ~$((i * 2)) s — http://localhost:$PORT"
    break
  fi
  sleep 2
done

if [ "$UP" != "1" ]; then
  echo "Avertissement : l'API n'a pas répondu après 40 s. Vérifier tmp/wiki_api.log"
fi
```

## Exemple d'appel une fois démarrée

```bash
curl -s "http://localhost:8091/search?theme=marketing&q=positionnement%20produit%20SaaS%20B2B&depth=1"
```

Paramètres : `theme`, `q` (ou `query`), `top_k` (défaut 10), `depth` (défaut 1),
`max_nodes` (défaut 80), `rephrase` (défaut true).

## Erreurs courantes

- Port déjà utilisé → vérifier `lsof -i :8091`
- Flask non installé → `uv run python -c "import flask"`
- Base RAG absente pour le thème → `/db_rag_update --theme {theme}`
- Reformulation lente/absente → la CLI `claude` doit être installée et authentifiée ; sinon l'API bascule sur la question brute (`rephrased: false`)
- Erreur au boot → consulter `tmp/wiki_api.log`
