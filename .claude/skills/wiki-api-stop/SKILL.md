# Skill — wiki-api-stop

## Déclenchement

Utiliser ce skill quand l'utilisateur veut arrêter l'API d'exploration du wiki.

Commande associée :

/wiki_api_stop

## Mission

1. Lire `tmp/wiki_api.pid`.
2. Envoyer SIGTERM au processus.
3. Supprimer `tmp/wiki_api.pid`.
4. Confirmer l'arrêt.

## Chemins

- PID : `tmp/wiki_api.pid`

## Commandes à exécuter

```bash
PID_FILE="$(pwd)/tmp/wiki_api.pid"

if [ ! -f "$PID_FILE" ]; then
  echo "Aucune API en cours (fichier PID introuvable)"
  exit 0
fi

PID=$(cat "$PID_FILE")

if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  echo "API arrêtée (PID $PID)"
else
  echo "Le processus $PID n'existe plus (déjà arrêté ?)"
fi

rm -f "$PID_FILE"
echo "Fichier PID supprimé"
```

## Erreurs courantes

- Fichier PID absent → l'API n'était pas lancée via `/wiki_api_start`
- PID invalide → l'API a peut-être planté, vérifier `tmp/wiki_api.log`
- Processus résiduel → `pkill -f wiki_api.py` en dernier recours
