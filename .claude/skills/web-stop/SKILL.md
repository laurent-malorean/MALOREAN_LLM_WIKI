# Skill — web-stop

## Déclenchement

Utiliser ce skill quand l'utilisateur veut arrêter le serveur de révision espacée.

Commande associée :

/web_stop

## Mission

1. Lire `tmp/website.pid`.
2. Envoyer SIGTERM au processus.
3. Supprimer `tmp/website.pid`.
4. Confirmer l'arrêt.

## Chemins

- PID : `tmp/website.pid`

## Commandes à exécuter

```bash
PID_FILE="$(pwd)/tmp/website.pid"

if [ ! -f "$PID_FILE" ]; then
  echo "Aucun serveur en cours (fichier PID introuvable)"
  exit 0
fi

PID=$(cat "$PID_FILE")

if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  echo "Serveur arrêté (PID $PID)"
else
  echo "Le processus $PID n'existe plus (déjà arrêté ?)"
fi

rm -f "$PID_FILE"
echo "Fichier PID supprimé"
```

## Erreurs courantes

- Fichier PID absent → le serveur n'était pas lancé via `/web_start`
- PID invalide → le serveur a peut-être planté, vérifier `tmp/website.log`
