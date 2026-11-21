#!/usr/bin/env python3
"""
Indexation incrémentale des notes du wiki dans LanceDB.

Usage:
    uv run python app/rag/rag_update.py [--theme THEME]
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

import lancedb
from sentence_transformers import SentenceTransformer

from rag_utils import (
    MODEL_NAME, PROJECT_ROOT, SCHEMA, VALID_THEMES,
    get_theme_paths, load_manifest, parse_note, save_manifest,
)


def write_log(log_dir: Path, db_dir: Path, manifest_path: Path, theme: str,
              added: list, updated: list, removed: list, total: int, duration: float) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    log_path = log_dir / f"{now.strftime('%Y-%m-%d')}-rag-update.md"

    lines = [
        f"# Log RAG update — {now.strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Résumé",
        "",
        f"- Thème : {theme}",
        f"- Notes scannées : {total + len(removed)}",
        f"- Notes ajoutées : {len(added)}",
        f"- Notes mises à jour : {len(updated)}",
        f"- Notes supprimées : {len(removed)}",
        f"- Total indexées : {total}",
        f"- Durée : {duration:.1f}s",
        "",
    ]

    lines += ["## Détail des ajouts", ""]
    lines += [f"- {i['id']} — {i['title']}" for i in added] or ["- (aucun)"]
    lines.append("")

    lines += ["## Détail des mises à jour", ""]
    lines += [f"- {i['id']} — {i['title']}" for i in updated] or ["- (aucune)"]
    lines.append("")

    lines += ["## Détail des suppressions", ""]
    lines += [f"- {p}" for p in removed] or ["- (aucune)"]
    lines.append("")

    lines += [
        "## Paramètres",
        "",
        f"- Modèle : {MODEL_NAME}",
        f"- DB : {db_dir.relative_to(PROJECT_ROOT)}",
        f"- Manifest : {manifest_path.relative_to(PROJECT_ROOT)}",
        "",
    ]

    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return log_path


def main():
    parser = argparse.ArgumentParser(description="Indexation RAG — wiki LDE_WIKI_IA")
    parser.add_argument("--theme", default="maintenance", choices=VALID_THEMES,
                        help="Thème cible (défaut : maintenance)")
    args = parser.parse_args()

    theme_root, db_dir, manifest_path, log_dir = get_theme_paths(args.theme)

    start = time.time()
    print(f"Chargement du modèle {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Ouverture de la base LanceDB ({args.theme})...")
    db_dir.parent.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(db_dir))

    if "notes" in db.table_names():
        table = db.open_table("notes")
    else:
        table = db.create_table("notes", schema=SCHEMA)

    manifest = load_manifest(manifest_path)
    notes_dir = theme_root / "notes"

    # Garde-fou de cohérence manifest / index.
    #
    # Le manifest sert à sauter les fichiers inchangés. S'il prétend que N notes
    # sont indexées alors que la table en contient bien moins, l'indexation
    # incrémentale ne réparera rien : elle sautera les fichiers manquants. On
    # repart donc d'un manifest vide pour forcer une reconstruction complète.
    indexed_rows = table.count_rows()
    if manifest and indexed_rows < 0.9 * len(manifest):
        print(
            f"Incohérence détectée : {indexed_rows} vecteurs en base pour "
            f"{len(manifest)} entrées au manifest."
        )
        print("Reconstruction complète forcée.")
        manifest = {}

    all_files = list(notes_dir.rglob("*.md"))
    current_paths = set()
    added = []
    updated = []
    records_to_upsert = []

    print(f"Scan de {len(all_files)} fichiers...")
    for path in all_files:
        rel = str(path.relative_to(PROJECT_ROOT))
        mtime = str(path.stat().st_mtime)
        current_paths.add(rel)

        prev = manifest.get(rel)
        if prev and prev.get("mtime") == mtime:
            continue

        note = parse_note(path)
        if note is None:
            continue

        vector = model.encode(
            f"passage: {note['text']}",
            normalize_embeddings=True
        ).tolist()

        records_to_upsert.append({**note, "vector": vector})

        if prev:
            updated.append({"id": note["id"], "title": note["title"]})
        else:
            added.append({"id": note["id"], "title": note["title"]})

        manifest[rel] = {"mtime": mtime, "id": note["id"]}

    removed_paths = [p for p in manifest if p not in current_paths]
    removed_ids = [manifest[p]["id"] for p in removed_paths]
    for p in removed_paths:
        del manifest[p]

    if records_to_upsert:
        print(f"Indexation de {len(records_to_upsert)} notes ({len(added)} nouvelles, {len(updated)} mises à jour)...")
        # Upsert atomique : une seule transaction qui met à jour les lignes
        # existantes et insère les nouvelles.
        #
        # Ne JAMAIS revenir à un enchaînement delete() puis add() : ces deux
        # opérations sont committées séparément, et toute interruption entre les
        # deux laisse l'index amputé des lignes supprimées. C'est la panne du
        # 2 octobre 2026, qui a réduit l'index maintenance de 995 à 17 vecteurs.
        (
            table.merge_insert("id")
            .when_matched_update_all()
            .when_not_matched_insert_all()
            .execute(records_to_upsert)
        )

    if removed_ids:
        print(f"Suppression de {len(removed_ids)} notes...")
        id_list = ", ".join(f"'{i}'" for i in removed_ids)
        try:
            table.delete(f"id IN ({id_list})")
        except Exception:
            pass

    total = len(manifest)
    save_manifest(manifest, manifest_path)

    duration = time.time() - start
    log_path = write_log(log_dir, db_dir, manifest_path, args.theme,
                         added, updated, removed_paths, total, duration)

    print()
    print(f"Terminé en {duration:.1f}s")
    print(f"  Ajoutées     : {len(added)}")
    print(f"  Mises à jour : {len(updated)}")
    print(f"  Supprimées   : {len(removed_paths)}")
    print(f"  Total indexées : {total}")
    print(f"  Log : {log_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
