# Skill — wiki-gap

## Déclenchement

Utiliser ce skill quand l'utilisateur veut détecter et combler les artefacts manquants dans le wiki après ingestion.

Commande associée :

/wiki_gap

## Paramètre thème

Ce skill accepte un paramètre `theme` (défaut : `maintenance`).
Thèmes valides : voir `data/wiki/themes.json`.

Tous les chemins `wiki/...` ci-dessous sont relatifs au thème : `data/wiki/themes/{theme}/`.
Les compteurs sont globaux : `data/wiki/counters.json`.

## Mission

Parcourir toutes les sources ingérées d'un thème, identifier les termes et idées qui auraient mérité une fiche dédiée mais n'en ont pas reçu, proposer une liste à l'utilisateur, puis créer les fiches validées.

## Artefacts gérés

- notes atomiques (ATO) ;
- glossaire (GLO) ;
- indicateurs (IND) ;
- processus métier (PRO) ;
- règles métier (BRL) ;
- textes réglementaires (REG) ;
- habilitations (HAB) ;
- objets métier (OBJ) ;
- normes (NOR) ;
- exigences normatives (EXN) ;
- MOC.

## Règles à lire

Toujours lire au démarrage :

- `.claude/rules/id-conventions.md`

Lire ensuite seulement les règles des types d'artefacts à créer :

- `.claude/rules/atomic-note.md`
- `.claude/rules/glossary-term.md`
- `.claude/rules/indicator.md`
- `.claude/rules/business-process.md`
- `.claude/rules/business-rule.md`
- `.claude/rules/regulatory-text.md`
- `.claude/rules/habilitation.md`
- `.claude/rules/domain-object.md`
- `.claude/rules/norm-reference.md`
- `.claude/rules/normative-requirement.md`
- `.claude/rules/moc.md`

## Pipeline

### Phase 1 — Charger le contexte

1. Lire `.claude/rules/id-conventions.md`.
2. Lire `data/generated/indexes/{theme}/sources.index.json` → filtrer les sources avec `ingested: true`.
3. Lire `data/generated/indexes/{theme}/artifacts.index.json` → charger l'index complet pour déduplication.
4. Lire `data/wiki/counters.json` → préparer les prochains IDs (compteurs globaux).

### Phase 2 — Analyser chaque source ingérée

Pour chaque source dont `ingested: true` :

**2a. Charger les données de la source**

- Lire la fiche source `data/wiki/themes/{theme}/sources/records/SRCXXXXX-slug.md`.
- Lire le rapport d'ingestion `data/generated/logs/wiki/{theme}/ingestion/SRCXXXXX-slug/ingestion-report.md` :
  sections utiles : artefacts créés, chunks sans extraction, points d'incertitude, prochaines actions.
- Lire `data/generated/logs/wiki/{theme}/ingestion/SRCXXXXX-slug/chunks.json` si disponible :
  identifier les chunks avec status "reference_technique", "skipped" ou notes indiquant un traitement sélectif.

**2b. Exploiter la vérification couverture du rapport**

- Lire la section "Vérification couverture" du rapport d'ingestion si elle existe.
- Identifier les chunks signalés comme problématiques :
  - chunks > 4 000 mots avec < 2 artefacts ;
  - chunks sans artefact hors référence technique ;
  - zones non couvertes.
- Pour chaque chunk signalé, relire le passage TXT correspondant (`data/wiki/themes/{theme}/sources/raw/txt/SRCXXXXX-slug.txt`) pour identifier les idées manquées.

**2c. Relire le TXT source si nécessaire**

- Priorité aux chunks, au rapport d'ingestion et au tableau de vérification (plus rapides et suffisants dans la plupart des cas).
- Relire les passages TXT correspondants uniquement si :
  - un chunk important indique un traitement sélectif ;
  - une section du rapport mentionne un domaine peu couvert ;
  - la couverture d'ingestion est inférieure à 90 % ;
  - le tableau de vérification signale des chunks à faible rendement.

**2d. Identifier les manques par type**

**GLO — Termes manquants :**
- Lister les termes explicitement définis ou normalisés dans la source (sections dédiées, phrases de définition, termes de normes).
- Vérifier via `artifacts.index.json` : fiche GLO existante pour ce terme ?
- Signaler si le terme est seulement absorbé dans une ATO, PRO ou IND sans fiche GLO propre.
- Qualifier si le terme est central, ambigu, récurrent ou structurant.
- Rappel : une ATO existante ne dispense pas de créer la GLO correspondante.

**ATO — Idées manquantes :**
- Identifier les idées distinctes dans les chunks traités sélectivement ou sans extraction.
- Vérifier qu'aucune ATO existante ne couvre déjà cette idée exacte.
- Critères : idée sourcée, compréhensible seule, réutilisable, titre propositionnel possible.

**IND — Indicateurs manquants :**
- Identifier les indicateurs cités ou définis sans fiche IND dédiée.
- Vérifier dans `artifacts.index.json`.

**PRO — Processus manquants :**
- Identifier les enchaînements métier décrits sans fiche PRO.
- Vérifier dans `artifacts.index.json`.

**BRL — Règles métier manquantes :**
- Identifier les contraintes ou décisions opératoires sans fiche BRL.
- Vérifier dans `artifacts.index.json`.

**REG — Textes réglementaires manquants :**
- Identifier les normes, directives, lois, décrets, classifications ou documents obligatoires cités sans fiche REG.
- Vérifier dans `artifacts.index.json`.

**HAB — Habilitations manquantes :**
- Identifier les permis, habilitations ou certifications cités sans fiche HAB.
- Vérifier dans `artifacts.index.json`.

**OBJ — Objets métier manquants :**
- Identifier les entités métier structurantes (équipement, BT, gamme, pièce de rechange) sans fiche OBJ.
- Vérifier dans `artifacts.index.json`.

**NOR — Normes manquantes :**
- Identifier les normes structurantes citées sans fiche NOR.
- Vérifier dans `artifacts.index.json`.

**EXN — Exigences normatives manquantes :**
- Identifier les obligations précises extraites de normes sans fiche EXN.
- Vérifier dans `artifacts.index.json`.

**MOC — Cartes de navigation manquantes :**
- Vérifier qu'un MOC existe pour chaque source ingérée.
- Vérifier dans `artifacts.index.json`.

**2e. Construire la liste des candidats**

Pour chaque candidat, noter :
- Numéro séquentiel (pour sélection utilisateur).
- Type (GLO / ATO / IND / PRO / BRL / REG / HAB / OBJ / NOR / EXN / MOC).
- Titre proposé (propositionnel pour ATO/BRL/PRO, terme pour GLO, nom pour IND/REG/HAB/OBJ/NOR/EXN/MOC).
- Source (SRCXXXXX + localisation approximative : chunk, section, page).
- Raison du manque (chunk non traité, choix restrictif, passe terminologique incomplète, etc.).
- Proximité avec artefacts existants si applicable.

### Phase 3 — Présenter la liste et demander validation

Afficher la liste complète des candidats groupée par source et par type :

```
## Source : SRC00002 — Le Grand Livre de la Maintenance

### GLO manquants
1. [ ] GLO — "maintenabilité" — terme central défini ch.3, absorbé dans ATO00012 sans fiche GLO propre
2. [ ] GLO — "taux de défaillance" — terme normalisé NF EN 13306, pas encore de fiche GLO

### ATO manquantes
3. [ ] ATO — "Le MTTR inclut les temps logistiques souvent négligés dans les calculs de disponibilité" — chunk C18, traité sélectivement

### IND manquants
4. [ ] IND — "MTTR — Mean Time To Repair" — cité dans plusieurs chunks, seul MTBF a sa fiche

### PRO manquants
(aucun identifié)

### BRL manquantes
(aucune identifiée)

### REG manquants
(aucun identifié)

### HAB manquantes
(aucune identifiée)

### OBJ manquants
(aucun identifié)

### NOR manquantes
(aucune identifiée)

### EXN manquantes
(aucune identifiée)

### MOC manquants
5. [ ] MOC — MOC de navigation pour SRC00002
```

Demander à l'utilisateur de sélectionner :
- "tout" — créer tous les candidats ;
- numéros séparés par des virgules (ex. "1,3,4") — créer une sélection ;
- "rien" — annuler sans création.

### Phase 4 — Créer les fiches sélectionnées

Pour chaque élément validé, dans l'ordre :

1. Lire les règles du type (`.claude/rules/[type].md`).
2. Lire `data/wiki/counters.json` → incrémenter le compteur du type.
3. Générer un UUID v4 pour `uid` et construire l'`id` (ex. GLO00021).
4. Créer la fiche complète dans le bon répertoire :
   - ATO → `data/wiki/themes/{theme}/notes/atomiques/`
   - GLO → `data/wiki/themes/{theme}/notes/glossaire/`
   - IND → `data/wiki/themes/{theme}/notes/indicateurs/`
   - PRO → `data/wiki/themes/{theme}/notes/processus/`
   - BRL → `data/wiki/themes/{theme}/notes/regles-metier/`
   - REG → `data/wiki/themes/{theme}/notes/regles-reglementaires/`
   - HAB → `data/wiki/themes/{theme}/notes/habilitations/`
   - OBJ → `data/wiki/themes/{theme}/notes/objets-metier/`
   - NOR → `data/wiki/themes/{theme}/notes/normes/`
   - EXN → `data/wiki/themes/{theme}/notes/exigences-normatives/`
   - MOC → `data/wiki/themes/{theme}/notes/moc/`
5. Mettre à jour `data/generated/indexes/{theme}/artifacts.index.json` (ajouter l'entrée).
6. Mettre à jour `data/wiki/counters.json` (sauvegarder le nouveau compteur).
7. Mettre à jour la fiche source `data/wiki/themes/{theme}/sources/records/SRCXXXXX-slug.md` :
   - Ajouter l'artefact dans le tableau `generated_artifacts` correspondant.
   - Mettre à jour `updated`.

### Phase 5 — Rapport de passe gap

Créer un rapport dans :

`data/generated/logs/wiki/{theme}/gap-analysis/YYYY-MM-DD-gap-report.md`

Format :

```markdown
# Rapport gap analysis — YYYY-MM-DD

## Sources analysées

- SRC00002 — Le Grand Livre de la Maintenance

## Candidats identifiés

| Type | Nombre |
|------|--------|
| ATO  | X      |
| GLO  | X      |
| IND  | X      |
| PRO  | X      |
| BRL  | X      |
| REG  | X      |
| HAB  | X      |
| OBJ  | X      |
| NOR  | X      |
| EXN  | X      |
| MOC  | X      |
| **Total** | **X** |

## Fiches créées

- GLO00021 — maintenabilité
- ATO00038 — ...

## Fiches écartées

- "terme X" — trop proche de GLO00005, enrichissement préférable

## Prochaines actions recommandées

-
```

## Règle anti-doublon

Avant de créer un artefact, toujours vérifier `artifacts.index.json`.

Si un artefact proche existe (même terme, même idée) : ne pas créer, signaler dans le rapport comme "écarté — doublon potentiel".

Ne jamais fusionner automatiquement.

## Règle de liens

Toujours ajouter des liens contextualisés dans les fiches créées.

Jamais de liens décoratifs sans explication.
