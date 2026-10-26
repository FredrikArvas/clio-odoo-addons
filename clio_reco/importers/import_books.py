"""Import av böcker från books_about_death.json → clio.media.work (work_type=Bok).

Upsert-nyckel: ISBN-identifierare (primär), annars title+author.
Kör: python import_books.py [--dry-run] [--file /annan/sökväg.json]
"""
import argparse
import json
import re
import sys
from pathlib import Path

from odoo_client import (
    ODOO_DB, ODOO_PASSWORD, connect,
    ensure_genre, ensure_work_type, find_work_by_identifier,
)

DEFAULT_JSON = Path(__file__).parent.parent.parent.parent.parent / (
    "Dropbox/projekt/Clio-projekt/Clio_Reco/books_about_death.json"
)

WORK_TYPE_NAME = "Bok"


def _safe_year(val) -> int | bool:
    if not val:
        return False
    try:
        return int(val)
    except (ValueError, TypeError):
        m = re.search(r'\d{3,4}', str(val))
        return int(m.group()) if m else False


def build_description(book: dict) -> str:
    parts = []
    if book.get("theme"):
        parts.append(f"<p><b>Tema:</b> {book['theme']}</p>")
    if book.get("description"):
        parts.append(f"<p>{book['description']}</p>")
    if book.get("relevance"):
        parts.append(f"<p><i>{book['relevance']}</i></p>")
    return "".join(parts)


def upsert_book(models, uid, book: dict, caches: dict, dry_run: bool) -> str:
    isbn = (book.get("isbn") or "").strip()
    title = book["title"].strip()
    author = book.get("author", "").strip()
    category = book.get("category", "Övrigt").strip()

    # Hitta befintlig post
    if dry_run:
        existing = []
    elif isbn:
        existing = find_work_by_identifier(models, uid, "isbn", isbn)
    else:
        existing = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "clio.media.work", "search",
            [[["name", "=", title], ["author", "=", author]]],
        )

    work_type_id = ensure_work_type(models, uid, WORK_TYPE_NAME, caches["work_type"]) if not dry_run else -1
    genre_id = ensure_genre(models, uid, category, caches["genre"]) if not dry_run else -1

    vals = {
        "name": title,
        "work_type_id": work_type_id,
        "author": author or False,
        "year": _safe_year(book.get("year")),
        "description": build_description(book),
        "genre_ids": [(4, genre_id)] if genre_id > 0 else [],
    }
    identifier_vals = {"scheme": "isbn", "value": isbn} if isbn else None

    if dry_run:
        action = "UPDATE" if existing else "CREATE"
        isbn_info = f" ISBN:{isbn}" if isbn else ""
        print(f"  [{action}] {title}{isbn_info}")
        return action.lower()

    if existing:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "clio.media.work", "write", [existing, vals])
        work_id = existing[0]
        action = "updated"
    else:
        work_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "clio.media.work", "create", [vals])
        action = "created"

    if identifier_vals and action == "created":
        identifier_vals["work_id"] = work_id
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "clio.media.work.identifier", "create", [identifier_vals])

    return action


def main():
    parser = argparse.ArgumentParser(description="Importera böcker till clio.media.work")
    parser.add_argument("--dry-run", action="store_true", help="Simulera utan att skriva till Odoo")
    parser.add_argument("--file", default=str(DEFAULT_JSON), help="Sökväg till JSON-fil")
    args = parser.parse_args()

    json_path = Path(args.file)
    if not json_path.exists():
        print(f"Filen hittades inte: {json_path}")
        sys.exit(1)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    books = data.get("books", [])
    print(f"Läser {len(books)} böcker från {json_path.name}")

    if args.dry_run:
        uid, models = None, None
        print("[DRY RUN — inga ändringar skrivs]")
    else:
        uid, models = connect()

    caches = {"work_type": {}, "genre": {}}
    counts = {"created": 0, "updated": 0}

    for book in books:
        result = upsert_book(models, uid, book, caches, args.dry_run)
        if result in counts:
            counts[result] += 1

    print(f"\nKlart: {counts['created']} skapade, {counts['updated']} uppdaterade")


if __name__ == "__main__":
    main()
