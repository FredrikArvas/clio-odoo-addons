"""Import av böcker (och andra verk) från JSON → clio.media.work.

JSON-format: import_schema_work.json (root-array).
Upsert-nyckel: source_ref (primär), sedan ISBN-identifierare, annars name+author.

Kör:
  python import_books.py --dry-run
  python import_books.py --file /sökväg/till/kurslitteratur.json
"""
import argparse
import json
import re
import sys
from pathlib import Path

from odoo_client import (
    ODOO_DB, ODOO_PASSWORD, connect,
    ensure_genre, ensure_work_type_by_code, find_work_by_identifier,
)


def _safe_year(val) -> int | bool:
    if not val:
        return False
    try:
        return int(val)
    except (ValueError, TypeError):
        m = re.search(r'\d{3,4}', str(val))
        return int(m.group()) if m else False


def _find_identifier(identifiers: list[dict], scheme: str) -> str:
    for ident in identifiers:
        if ident.get("scheme") == scheme:
            return ident["value"]
    return ""


def upsert_work(models, uid, item: dict, caches: dict, dry_run: bool) -> str:
    name = item["name"].strip()
    work_type_code = item["work_type"]
    author = (item.get("author") or "").strip()
    source_ref = (item.get("source_ref") or "").strip() or False
    genres = item.get("genres") or []
    identifiers = item.get("identifiers") or []
    isbn = _find_identifier(identifiers, "isbn")

    # ── Hitta befintlig post ─────────────────────────────────────────────────────
    existing = []
    if not dry_run:
        if source_ref:
            existing = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                "clio.media.work", "search",
                [[["source_ref", "=", source_ref]]],
            )
        if not existing and isbn:
            existing = find_work_by_identifier(models, uid, "isbn", isbn)
        if not existing:
            existing = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                "clio.media.work", "search",
                [[["name", "=", name], ["author", "=", author or False]]],
            )

    # ── Bygg värden ──────────────────────────────────────────────────────────────
    work_type_id = (
        ensure_work_type_by_code(models, uid, work_type_code, caches["work_type"])
        if not dry_run else -1
    )

    genre_ids_cmd = []
    for genre_name in genres:
        if not dry_run:
            gid = ensure_genre(models, uid, genre_name, caches["genre"])
            genre_ids_cmd.append((4, gid))

    vals = {
        "name": name,
        "work_type_id": work_type_id,
        "author": author or False,
        "year": _safe_year(item.get("year")),
        "description": item.get("description") or False,
        "genre_ids": genre_ids_cmd,
    }
    if source_ref:
        vals["source_ref"] = source_ref

    # ── Dry run ──────────────────────────────────────────────────────────────────
    if dry_run:
        action = "UPDATE" if existing else "CREATE"
        isbn_info = f" ISBN:{isbn}" if isbn else ""
        ref_info = f" ref:{source_ref}" if source_ref else ""
        print(f"  [{action}] {name}{isbn_info}{ref_info}")
        return action.lower()

    # ── Skriv till Odoo ───────────────────────────────────────────────────────────
    if existing:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "clio.media.work", "write", [existing, vals])
        work_id = existing[0]
        action = "updated"
    else:
        work_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "clio.media.work", "create", [vals])
        action = "created"

    # Identifierare läggs bara till vid create (uppdateras inte automatiskt)
    if action == "created":
        for ident in identifiers:
            scheme = ident.get("scheme")
            value = (ident.get("value") or "").strip()
            if scheme and value:
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    "clio.media.work.identifier", "create",
                    [{"work_id": work_id, "scheme": scheme, "value": value}],
                )

    return action


def main():
    parser = argparse.ArgumentParser(description="Importera verk till clio.media.work")
    parser.add_argument("--dry-run", action="store_true", help="Simulera utan att skriva till Odoo")
    parser.add_argument("--file", required=True, help="Sökväg till JSON-fil (import_schema_work.json-format)")
    args = parser.parse_args()

    json_path = Path(args.file)
    if not json_path.exists():
        print(f"Filen hittades inte: {json_path}")
        sys.exit(1)

    items = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(items, list):
        print("JSON-filen ska vara en root-array av verk.")
        sys.exit(1)

    print(f"Läser {len(items)} verk från {json_path.name}")

    if args.dry_run:
        uid, models = None, None
        print("[DRY RUN — inga ändringar skrivs]")
    else:
        uid, models = connect()

    caches = {"work_type": {}, "genre": {}}
    counts = {"created": 0, "updated": 0}
    errors = 0

    for item in items:
        try:
            result = upsert_work(models, uid, item, caches, args.dry_run)
            if result in counts:
                counts[result] += 1
        except Exception as exc:
            name = item.get("name", "?")
            print(f"  [FEL] {name}: {exc}")
            errors += 1

    print(f"\nKlart: {counts['created']} skapade, {counts['updated']} uppdaterade, {errors} fel")


if __name__ == "__main__":
    main()
