# /mobileapp_build

Utiliser le skill `.claude/skills/mobileapp-build/SKILL.md`.

Objectif :

- Lire les notes dues depuis `data/generated/indexes/{theme}/artifacts.index.json` et `data/generated/website/review_state.json`.
- Embarquer le contenu de toutes les notes dues dans un fichier HTML autonome.
- Générer `data/generated/mobileapp/mobile.html` utilisable hors ligne sur smartphone.
- Afficher le nombre de notes embarquées et le chemin du fichier.
