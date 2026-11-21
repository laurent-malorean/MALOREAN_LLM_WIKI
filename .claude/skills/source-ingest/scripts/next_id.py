#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import sys
import uuid

WIKI_ROOT = Path.cwd() / "data" / "wiki"


def reserve_ids(prefix: str, count: int) -> list[str]:
    """Réserve `count` identifiants consécutifs et met à jour le compteur global."""
    counters_path = WIKI_ROOT / "counters.json"
    counters_path.parent.mkdir(parents=True, exist_ok=True)

    if counters_path.exists():
        counters = json.loads(counters_path.read_text(encoding="utf-8"))
    else:
        counters = {}

    start = int(counters.get(prefix, 0)) + 1
    counters[prefix] = start + count - 1
    counters_path.write_text(
        json.dumps(counters, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return [f"{prefix}{n:05d}" for n in range(start, start + count)]


def next_id(prefix: str) -> str:
    return reserve_ids(prefix, 1)[0]


def main():
    parser = argparse.ArgumentParser(
        description="Réserve un ou plusieurs identifiants humains (et, en option, un UUID technique par identifiant)."
    )
    parser.add_argument("prefix", help="Préfixe 3 lettres (ATO, GLO, REG...).")
    parser.add_argument(
        "--count", type=int, default=1, help="Nombre d'identifiants à réserver (défaut : 1)."
    )
    parser.add_argument(
        "--with-uid",
        action="store_true",
        help="Imprime aussi un UUID technique par identifiant, séparé par une tabulation : ID<TAB>UUID.",
    )
    args = parser.parse_args()

    if args.count < 1:
        print("--count doit être >= 1", file=sys.stderr)
        sys.exit(1)

    ids = reserve_ids(args.prefix, args.count)
    for id_ in ids:
        if args.with_uid:
            print(f"{id_}\t{uuid.uuid4()}")
        else:
            print(id_)


if __name__ == "__main__":
    main()
