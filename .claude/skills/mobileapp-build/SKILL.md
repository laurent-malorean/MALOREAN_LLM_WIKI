# Skill — mobileapp-build

## Déclenchement

Utiliser ce skill quand l'utilisateur veut générer la version mobile hors ligne du wiki.

Commande associée :

/mobileapp_build

## Paramètre thème

Ce skill accepte un paramètre `theme` (défaut : `maintenance`).
Thèmes valides : voir `data/wiki/themes.json`.

## Mission

Générer un fichier HTML unique et autonome `data/generated/mobileapp/mobile.html` utilisable hors ligne sur smartphone.

Le fichier contient :
- Toutes les notes dues embarquées en JSON dans une `<script>` tag
- CSS et JS inline, zéro dépendance externe, zéro fetch
- Un seul bouton **Suivant** pour passer à la note suivante
- Rendu Markdown basique (titres, listes, paragraphes)

## Étapes

1. Exécuter le script de génération :

```bash
uv run python \
  ".claude/skills/mobileapp-build/scripts/generate_mobile.py"
```

2. Vérifier que `data/generated/mobileapp/mobile.html` a été créé.
3. Indiquer le nombre de notes embarquées et le chemin du fichier généré.

## Chemins

- Script : `.claude/skills/mobileapp-build/scripts/generate_mobile.py`
- Sortie : `data/generated/mobileapp/mobile.html`
- Index artifacts : `data/generated/indexes/{theme}/artifacts.index.json`
- État révision : `data/generated/website/review_state.json`
- Notes wiki : `data/wiki/themes/{theme}/notes/`

## Erreurs courantes

- `artifacts.index.json` absent → lancer `/wiki_lint` pour reconstruire l'index
- Note Markdown introuvable → le script ignore la note et continue
