# Skill — web-start

## Déclenchement

Utiliser ce skill quand l'utilisateur veut démarrer le serveur de révision espacée.

Commande associée :

/web_start

## Mission

1. Vérifier si le serveur est déjà lancé (lire `tmp/website.pid` si existant, tester avec `kill -0 $PID`).
2. Si déjà lancé, informer l'utilisateur et ne rien faire.
3. Lancer `app/website/server.py` en arrière-plan avec `uv run` du projet.
4. Stocker le PID dans `tmp/website.pid`.
5. Rediriger les logs vers `tmp/website.log`.
6. Confirmer que le serveur répond sur `http://localhost:8083`.

## Chemins

- Interpréteur : `uv run python`
- Script : `app/website/server.py`
- PID : `tmp/website.pid`
- Log : `tmp/website.log`

## Commandes à exécuter

```bash
# Vérifier si déjà lancé
PID_FILE="$(pwd)/tmp/website.pid"
if [ -f "$PID_FILE" ]; then
  EXISTING_PID=$(cat "$PID_FILE")
  if kill -0 "$EXISTING_PID" 2>/dev/null; then
    echo "Serveur déjà lancé (PID $EXISTING_PID) — http://localhost:8083"
    exit 0
  fi
fi

# Lancer le serveur
uv run python \
  "app/website/server.py" \
  >> "$(pwd)/tmp/website.log" \
  2>&1 &

echo $! > "$PID_FILE"
echo "Serveur démarré (PID $(cat $PID_FILE))"

# Attendre le démarrage
sleep 2

# Vérifier
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8083/ 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
  echo "Serveur OK — http://localhost:8083"
else
  echo "Avertissement : code HTTP $HTTP_CODE. Vérifier tmp/website.log"
fi
```

## Erreurs courantes

- Port déjà utilisé → vérifier `lsof -i :8083`
- Flask non installé → vérifier avec `uv run python -c "import flask"`
- Erreur de parsing → consulter `tmp/website.log`
