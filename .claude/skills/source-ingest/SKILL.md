# Skill — source-ingest

## Déclenchement

Utiliser ce skill quand l'utilisateur veut analyser une source TXT déjà ajoutée.

Commande associée :

/source_ingest

## Paramètre thème

Ce skill accepte un paramètre `theme` (défaut : `maintenance`).
Thèmes valides : voir `data/wiki/themes.json`.

Tous les chemins ci-dessous sont relatifs à `data/wiki/themes/{theme}/`.
Les compteurs sont globaux : `data/wiki/counters.json`.

## Mission

Analyser une source TXT pour créer ou mettre à jour les artefacts du wiki, en
extrayant **toutes les idées atomiques distinctes** — sans en manquer, et sans
produire de doublons.

## Principe directeur : un seul fil, mémoire cumulative, séquentiel

Ce skill reproduit une lecture humaine attentive, PAS une armée d'agents.

> **NE JAMAIS** paralléliser l'extraction en lançant un sous-agent par section
> (fan-out). Des agents qui ne se voient pas re-proposent les mêmes idées
> (surtout dans les livres répétitifs), ce qui gonfle artificiellement le compte,
> force une déduplication coûteuse, et fait exploser la consommation de tokens en
> rechargeant le contexte anti-duplication à chaque agent.

À la place, l'agent principal (ce fil de conversation) travaille **seul et en
série** :

1. Il charge **une seule fois** la liste des idées déjà présentes dans le wiki.
2. Il tient, tout au long de la source, une **liste cumulative des idées déjà
   retenues dans cette session** (les nouvelles ATO décidées).
3. Il lit les sections **l'une après l'autre**. Pour chaque idée rencontrée, il
   la compare à l'anti-dup initial ET à la liste cumulative de la session, puis
   choisit **l'une des quatre issues** :
   - **idée nouvelle** (absente des deux) → créer une ATO ;
   - **idée déjà couverte, et la source apporte une nuance / preuve / contre-exemple
     nouveau** → **enrichir** l'ATO existante (corps) ET ajouter cette source à son
     `source_ids` ;
   - **idée déjà couverte, sans apport conceptuel nouveau** → ne PAS ignorer
     purement : **ajouter cette source au `source_ids`** de l'ATO existante
     (corroboration multi-sources, traçabilité) ;
   - **hors sujet / promotionnel** → ignorer.
   L'enrichissement et l'ajout de source s'appliquent aussi bien aux ATO créées
   **avant** cet appel (accrétion inter-sources, voir atomic-note.md) qu'à celles
   créées plus tôt dans la même session.
4. Comme la mémoire est cumulative, **aucun doublon n'est généré** : il n'y a
   donc pas de passe de déduplication a posteriori.

La lenteur (traitement en série) est acceptable et voulue. L'objectif est la
couverture complète des idées **distinctes** au coût token le plus bas, pas la
vitesse ni le volume brut.

Ordre de grandeur attendu : le ratio « ATO ajoutées ÷ ATO d'origine » d'un
retraitement se situe typiquement entre ×1,5 et ×3. Un chiffre nettement
supérieur (ex. ×5+) est un **signal à vérifier, pas un interdit** : relire les
idées retenues et fusionner celles qui partagent le même foyer conceptuel. Un
ratio élevé reste **légitime** si l'ingestion initiale était très pauvre (ex. une
poignée d'ATO pour un livre dense) — dans ce cas le documenter dans le rapport
plutôt que de rogner artificiellement.

## Artefacts gérés

- notes atomiques (ATO) — cœur, via la méthode séquentielle ci-dessous ;
- glossaire (GLO), normes (NOR), exigences normatives (EXN), processus (PRO),
  objets métier (OBJ), règles métier (BRL), textes réglementaires (REG),
  habilitations (HAB), indicateurs (IND), MOC — par passes dédiées.

## Règles à lire

Toujours lire :

- `.claude/rules/id-conventions.md`
- `.claude/rules/source-file.md`
- `.claude/rules/linking-rules.md`
- `.claude/rules/chunking-strategy.md`
- `.claude/rules/atomic-note.md`
- `.claude/rules/ingestion-report.md`

Lire ensuite selon le contenu de la source :

- `.claude/rules/glossary-term.md`
- `.claude/rules/norm-reference.md`
- `.claude/rules/normative-requirement.md`
- `.claude/rules/business-process.md`
- `.claude/rules/domain-object.md`
- `.claude/rules/business-rule.md`
- `.claude/rules/regulatory-text.md`
- `.claude/rules/habilitation.md`
- `.claude/rules/indicator.md`
- `.claude/rules/moc.md`

## Outils

- `scripts/chunk_source.py` — segmente le TXT en chunks contrôlés (≤ 6000 mots)
  et écrit `chunks/chunk-NNNN.txt` + un manifest.
- `scripts/existing_ideas.py` — dresse **une seule fois** la liste des ATO+GLO
  déjà présentes (anti-dup), pour le thème (et thèmes voisins via `--also`).
- `scripts/next_id.py` — réserve des identifiants dans `counters.json`.
  `next_id.py ATO --count N --with-uid` réserve N IDs d'un coup et imprime, pour
  chacun, `ID<TAB>UUID` (le double identifiant complet, voir id-conventions.md).
  **Toujours utiliser `--with-uid`** : c'est cet UUID qui doit remplir le champ
  `uid` de chaque note, jamais laissé vide.
- `scripts/update_sources_index.py`, `scripts/generate_backlinks.py`,
  `scripts/update_indexes.py` — bookkeeping.

## Pipeline

### 0. Préparation (une fois)

1. Identifier la fiche source (`sources/records/SRCxxxxx-*.md`) et son TXT.
   Repérer son MOC (`notes/moc/`).
2. Segmenter le TXT :
   `uv run python .claude/skills/source-ingest/scripts/chunk_source.py <txt> data/generated/logs/wiki/{theme}/ingestion/SRCxxxxx-slug/chunks.json`
   (vérifier qu'aucun chunk ne dépasse 6000 mots ; voir chunking-strategy.md).
3. Charger **une seule fois** l'anti-dup :
   `uv run python .claude/skills/source-ingest/scripts/existing_ideas.py --theme {theme} [--also <theme2>] --out <scratch>/existing_ideas.txt`
   puis **lire ce fichier une fois** et le garder en tête. Ne pas le relire à
   chaque idée.
4. Ouvrir une **liste cumulative de session** (vide au départ) : elle recensera
   chaque idée atomique retenue au fil des sections (titre proposé + section
   d'origine). C'est la mémoire qui empêche les doublons.

### 1. Extraction séquentielle — une seule lecture de la source

Chaque chunk n'est lu **qu'une seule fois**. Pendant cette lecture unique, relever
**tous les types d'artefacts à la fois** (ne pas relire le chunk pour un second
type — c'est du gaspillage de tokens).

Pour chaque chunk, **dans l'ordre**, un par un (jamais en parallèle) :

0. Avant de traiter le chunk, **se remémorer la liste cumulative de session**
   (idées déjà retenues) : c'est elle qui arme l'anti-doublon interne. Sur une
   source longue, cette liste grossit — la garder présente à l'esprit à chaque
   chunk est ce qui empêche un chunk tardif de re-proposer une idée d'un chunk
   antérieur.
1. Lire le chunk **une fois**.
2. **ATO** — identifier les idées atomiques candidates (test atomique : une
   proposition autonome, compréhensible hors source, réutilisable — voir
   atomic-note.md). Pour chaque candidate, comparer le FOND (pas les mots) à
   l'anti-dup initial ET à la liste cumulative de session, puis appliquer les
   quatre issues du principe directeur : **créer** (nouvelle) ; **enrichir +
   ajouter la source** (déjà couverte, apport nouveau) ; **ajouter seulement la
   source** au `source_ids` de l'ATO existante (déjà couverte, sans apport —
   corroboration) ; **ignorer** (hors sujet/promotionnel).
3. **Autres types, dans la même lecture** — repérer aussi, sans relire le chunk :
   - **GLO** : termes définis explicitement, ou apparaissant dans le titre/slug
     d'un artefact, normalisés, ou formes/opérations de maintenance / indicateurs ;
   - **REG/HAB/EXN** : directives (`YYYY/NN/CE`), textes légaux (`décret`,
     `article R.`, `article L.`, `Code du travail`, `arrêté`), documents
     obligatoires (`DU`, `EDD`, `POI`, `PPI`), classifications (`ICPE`, `ATEX`,
     `Seveso`), habilitations (`permis de feu`, `habilitation électrique`,
     `travail en hauteur`, `espace confiné`, `radioprotection`) ;
   - **NOR / PRO / OBJ / BRL / IND** selon le contenu (voir les rules).
   `existing_ideas.txt` ne couvre que ATO + GLO. Pour les types REG/HAB/EXN/PRO/
   NOR/OBJ/BRL/IND, vérifier l'anti-dup directement dans
   `data/generated/indexes/{theme}/artifacts.index.json` avant de retenir un candidat.
4. Ajouter chaque ATO **créée** à la liste cumulative **immédiatement**, avant de
   passer au chunk suivant (c'est ce report qui évite qu'un chunk ultérieur
   reproduise la même idée). Tenir en parallèle les listes des artefacts à créer
   par type, et des ATO existantes à enrichir/re-sourcer.
5. Ne pas écrire les fichiers à ce stade — accumuler d'abord toutes les listes.

Discipline anti-sur-comptage : préférer **enrichir** une idée déjà retenue plutôt
que d'en créer une quasi-jumelle. Une même thèse reformulée sous un autre angle
n'est PAS une nouvelle ATO.

**Zéro idée nouvelle est un résultat valide.** Si une source déjà bien ingérée
n'apporte aucune idée atomique inédite, ne rien forcer : se contenter d'ajouter la
source aux `source_ids` des ATO qu'elle corrobore, et le documenter dans le
rapport. Ne jamais inventer des ATO pour « faire du chiffre ».

### 2. Passe terminologique finale — légère, SANS relire la source

Ne relit **pas** les chunks. Sur la seule base de la liste des ATO créées (leurs
titres/slugs) et de `data/generated/indexes/{theme}/artifacts.index.json`, se demander :
quels termes structurants ont été utilisés/définis dans les ATO mais n'ont pas
encore de fiche GLO ? Créer les GLO manquantes. Une ATO/PRO/IND existante ne
dispense PAS de la GLO correspondante (types complémentaires). Cette passe rattrape
les termes « absorbés » dans une note sans fiche propre — elle coûte peu car elle
ne rouvre pas le texte source.

### 3. Validation et écriture

Une fois la liste cumulative finale arrêtée :

1. Réserver **un ID et un UUID par note** à créer, en une commande :
   `uv run python .claude/skills/source-ingest/scripts/next_id.py ATO --count N --with-uid`
   Chaque ligne renvoie `ID<TAB>UUID`. Les IDs ne sont jamais réutilisés. Garder
   la correspondance `ID → UUID` : le champ `uid` de chaque note se remplit avec
   son UUID **dès la création** — ne jamais écrire `uid: ""` (le lint rejette les
   `missing_uid`, et un correctif a posteriori est du gaspillage).
2. **Validation atomique — condition BLOQUANTE d'écriture.** Avant d'écrire une
   note, remplir sa section `## Validation atomique` (voir atomic-note.md) en
   **justifiant chaque critère par une preuve concrète tirée de la note**, jamais
   par un « oui » sec :
   - *Une seule idée principale* : énoncer l'idée en une phrase ; si on ne peut
     pas, c'est qu'il y en a plusieurs → **splitter**.
   - *Titre propositionnel* : le titre affirme une thèse (pas un mot vague).
   - *Compréhensible hors source* : citer ce qui rend la note autoportante.
   - *Source traçable* : `source_ids` + localisation renseignés.
   - *Réutilisable* : dire dans quel autre contexte l'idée sert.
   - *Liens contextualisés* : 2 à 4 liens `[[ID-slug]]` avec relation explicite.
   - *Verdict* : « valide » **seulement si tous les critères sont satisfaits**.
   Si le verdict n'est pas « valide », **ne pas écrire la note** : la splitter en
   idées atomiques distinctes, la reformuler, ou l'abandonner. Une note dont la
   validation est cochée « oui » sans justification est un échec du skill.
3. Écrire chaque note validée (frontmatter complet + sections de atomic-note.md,
   corps en français si le thème l'exige). Renseigner `uid` avec l'UUID réservé à
   l'étape 3.1 (**jamais `uid: ""`**) et `id` avec l'identifiant humain
   correspondant. Liens `[[ID-slug]]` uniquement dans le corps. Appliquer aussi
   les enrichissements / ajouts de `source_ids` décidés à l'étape 1 sur les ATO
   existantes.
4. Écrire les artefacts des autres types (GLO, REG, HAB, PRO…) en respectant le
   gabarit et les critères d'inclusion de **leur rule dédiée** (glossary-term.md,
   regulatory-text.md, etc.) — la validation atomique ci-dessus est propre aux ATO.

### 4. Bookkeeping

1. **Vérifier les slugs réels — BLOQUANT — avant d'écrire MOC et fiche source.**
   Les notes ATO sont déjà écrites (étape 3) ; c'est en écrivant le MOC et la
   fiche source, qui *pointent* vers elles, qu'il faut des slugs exacts. `Glob`
   sur `notes/atomiques/ATO*.md`, `notes/glossaire/GLO*.md`, `notes/moc/MOC*.md`
   → table `ID → slug-réel` depuis le disque uniquement. N'utiliser que ces slugs.
   Après écriture du MOC, extraire ses slugs (`\[\[([^\]]+)\]\]`) et corriger tout
   lien mort.
2. Mettre à jour la fiche source (`generated_artifacts.atomic_notes` en
   frontmatter + corps, `ingestion_coverage`, `updated`, note de passe).
3. `uv run python .claude/skills/source-ingest/scripts/update_sources_index.py --theme {theme}`
4. `uv run python .claude/skills/source-ingest/scripts/generate_backlinks.py --theme {theme}`
5. Mettre à jour `data/generated/indexes/{theme}/artifacts.index.json` et le MOC de la source.
6. Rapport dans `data/generated/logs/wiki/{theme}/ingestion/` (voir ingestion-report.md) :
   documenter le nombre d'idées retenues, le ratio de découverte, les ATO
   existantes enrichies/re-sourcées, et tout regroupement anti-sur-comptage.
7. Corriger les slugs : `uv run python .claude/scripts/fix-broken-slugs.py`
8. **Lint** : `uv run python .claude/skills/wiki-lint/scripts/lint_wiki.py --theme {theme}`
   puis corriger tout lien cassé (slug erroné, ou cible cross-thème à remplacer
   par une cible du thème). Relancer jusqu'à « Aucun problème détecté ».

## Garde-fous chunks

- Aucun chunk > 6000 mots (voir chunking-strategy.md ; sous-découper sinon).
- La classification « référence technique » ne s'applique qu'aux passages
  intégralement calculatoires (formules, tables numériques, démonstrations). Ne
  jamais classer « référence technique » un contenu méthodologique ou technique :
  son principe propre peut être une ATO distincte.

## Règle de liaison

Liens créés **exclusivement dans le corps** des notes, jamais en frontmatter
(pas de bloc `links:`, `linked_atomic_notes:`, `norm_file:`, ni IDs LDE dans
`relations.*` des NOR — seuls les codes officiels externes y restent). Chaque
lien porte une explication : `[[ID-slug]] — relation`. La section
`## Notes qui pointent ici` est complétée par `generate_backlinks.py`.

## Règle anti-doublon

L'anti-dup a deux niveaux, tenus par le fil unique :
- **externe** : `existing_ideas.txt` (idées déjà dans le wiki), lu une fois ;
- **interne** : la liste cumulative de session (idées déjà retenues cette fois).
Ne créer une ATO que si l'idée est absente des deux. Si l'idée est déjà couverte,
ne pas se contenter de l'ignorer : **enrichir l'ATO existante** si la source
apporte du neuf, et dans tous les cas **ajouter la source à son `source_ids`**
(une idée corroborée par plusieurs sources doit le tracer). En cas de doute,
enrichir plutôt que dupliquer. Ne jamais fusionner d'artefacts existants
automatiquement — consigner les fusions dans `inbox/fusions-proposees.md`.

## Reprise après compaction ou coupure de session

- **Ne pas faire confiance** aux slugs/titres mentionnés dans un résumé.
- Reconstruire l'état depuis le **disque** : quelles ATO existent déjà dans la
  plage d'IDs réservée ? Ne ré-écrire que les manquantes.
- Reconstruire la liste cumulative de session en relisant les notes déjà écrites
  pour cette source (leur `source_ids` + leurs titres) avant de reprendre.
- Vérifier `data/wiki/counters.json` (IDs réservés jamais réutilisés, même si
  l'écriture a échoué).
- Appliquer systématiquement la vérification des slugs sur disque (bookkeeping,
  étape 4.1) avant de (ré)écrire MOC ou fiche source.

## Vérification de couverture (dans le rapport)

- nombre d'idées retenues et ratio de découverte (alerte si ≫ ×3) ;
- regroupements effectués pour éviter le sur-comptage ;
- chunks sans idée nouvelle (et pourquoi) ;
- zones non couvertes (contenu strictement promotionnel exclu à dessein).
