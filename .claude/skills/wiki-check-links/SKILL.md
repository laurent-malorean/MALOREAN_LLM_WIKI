# Skill — wiki-check-links

## Déclenchement

Utiliser ce skill quand l'utilisateur veut lister les liens cassés du wiki.

Commande associée :

/wiki_check_links

## Paramètre thème

Ce skill accepte un paramètre `theme` (défaut : `maintenance`).
Thèmes valides : voir `data/wiki/themes.json`.

## Mission

Détecter tous les liens `[[...]]` qui pointent vers une note inexistante dans un thème, sans modifier aucun fichier.

## Exécution

Lancer le script Python standalone depuis la racine du projet :

```
uv run python .claude/skills/wiki-check-links/scripts/check_links.py --theme {theme}
```

Options :
- `--theme THEME` : thème cible (défaut : maintenance)
- `--summary` : une ligne par cible manquante, sans détail des fichiers

## Sortie

Afficher le résultat du script directement dans le terminal.

Ne pas créer de rapport, ne pas modifier de fichiers.

## Exemple de sortie

```
— 3 cibles manquantes, 5 occurrences —

  [[GLO00109-kaizen]]  (2 occurrences)
    notes/glossaire/GLO00232-jishuken.md
    notes/glossaire/GLO00245-entropie-organisationnelle.md
  [[ATO00118-microdefaillances]]  (1 occurrence)
    notes/atomiques/ATO00132-automaintenance.md
```

Ou si tout est propre :

```
✓ Aucun lien cassé détecté.
```
