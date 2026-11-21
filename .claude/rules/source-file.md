# Règles — Fiche source

> Les chemins ci-dessous sont relatifs à la racine du thème (`data/wiki/themes/{theme}/`).

## Objectif

Une fiche source documente un document d'origine ajouté au wiki.

Elle ne doit pas être une synthèse complète.

Elle doit servir à tracer :

- le PDF original ;
- le TXT extrait ;
- le statut d'ingestion ;
- les artefacts générés à partir de cette source ;
- les logs associés.

## Emplacement

Les fiches sources sont dans :

sources/records/

Les PDF originaux sont dans :

sources/raw/pdf/

Les TXT extraits sont dans :

sources/raw/txt/

## Format

Chaque fiche source doit suivre ce modèle :

---
uid: ""
id: "SRC00000"
type: "source_record"
status: "added"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"

source:
  title: ""
  author: ""
  organization: ""
  publication_date: ""
  source_type: "pdf"
  language: "fr"
  domain: []
  reliability: "unknown"
  confidence: "low"

files:
  raw_pdf: ""
  raw_txt: ""
  original_filename: ""
  checksum: ""
  page_count: ""
  text_extraction_status: "success"

processing:
  added_by: "source_add"
  ingested: false
  ingestion_status: "not_started"
  last_ingested_at: ""
  ingestion_coverage: 0

generated_artifacts:
  atomic_notes: []
  glossary_terms: []
  norms: []
  normative_requirements: []
  business_processes: []
  domain_objects: []
  business_rules: []
  indicators: []
  mocs: []

logs:
  source_add_log: ""
  ingestion_logs: []
---

# Source — Titre du document

## Résumé administratif

Document ajouté au wiki.

## Fichiers associés

- PDF original :
- Texte extrait :

## État de traitement

- Conversion texte :
- Ingestion :
- Couverture :

## Artefacts générés depuis cette source

### Notes atomiques

Aucune pour l'instant.

### Glossaire

Aucun pour l'instant.

### Normes

Aucune pour l'instant.

### Exigences normatives

Aucune pour l'instant.

### Processus métier

Aucun pour l'instant.

### Objets métier

Aucun pour l'instant.

### Règles métier

Aucune pour l'instant.

### Indicateurs

Aucun pour l'instant.

### MOC

Aucun pour l'instant.

## Notes de traitement

-

## Règle

La fiche source doit être mise à jour après chaque ingestion.
