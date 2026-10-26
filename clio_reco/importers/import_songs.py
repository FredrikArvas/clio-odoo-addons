"""Import av låtar från death_songs.json → clio.media.work (work_type=Låt).

Upsert-nyckel: Spotify-URL-identifierare (primär), annars name.
Kör: python import_songs.py [--dry-run] [--file /annan/sökväg.json]
"""
import argparse
import json
import sys
from pathlib import Path

from odoo_client import (
    ODOO_DB, ODOO_PASSWORD, connect,
    ensure_genre, ensure_work_type, find_work_by_identifier,
)

DEFAULT_JSON = Path(__file__).parent.parent.parent.parent.parent / (
    "Dropbox/projekt/Clio-projekt/Clio_Reco/death_songs.json"
)

WORK_TYPE_NAME = "Låt"


def upsert_song(models, uid, track: dict, caches: dict, dry_run: bool) -> str:
    title = track["title"].strip()
    artist = track.get("artist", "").strip()
    name = f"{title} — {artist}" if artist else title
    url = (track.get("spotify_url") or "").strip()
    genre_str = track.get("genre", "Övrigt").strip()
    theme = (track.get("theme") or "").strip()

    if dry_run:
        existing = []
    elif url:
        existing = find_work_by_identifier(models, uid, "spotify", url)
    else:
        existing = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "clio.media.work", "search",
            [[["name", "=", name]]],
        )

    work_type_id = ensure_work_type(models, uid, WORK_TYPE_NAME, caches["work_type"]) if not dry_run else -1

    genre_names = [g.strip() for g in genre_str.replace("/", ",").split(",") if g.strip()]
    genre_ids = []
    for gname in genre_names:
        gid = ensure_genre(models, uid, gname, caches["genre"]) if not dry_run else -1
        if gid > 0:
            genre_ids.append((4, gid))

    vals = {
        "name": name,
        "work_type_id": work_type_id,
        "author": artist or False,
        "description": f"<p><b>Tema:</b> {theme}</p>" if theme else False,
        "genre_ids": genre_ids,
    }

    if dry_run:
        action = "UPDATE" if existing else "CREATE"
        print(f"  [{action}] {name}")
        return action.lower()

    if existing:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "clio.media.work", "write", [existing, vals])
        action = "updated"
        work_id = existing[0]
    else:
        work_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "clio.media.work", "create", [vals])
        action = "created"

    if url and action == "created":
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "clio.media.work.identifier", "create",
            [{"work_id": work_id, "scheme": "spotify", "value": url}],
        )

    return action


def main():
    parser = argparse.ArgumentParser(description="Importera låtar till clio.media.work")
    parser.add_argument("--dry-run", action="store_true", help="Simulera utan att skriva till Odoo")
    parser.add_argument("--file", default=str(DEFAULT_JSON), help="Sökväg till JSON-fil")
    args = parser.parse_args()

    json_path = Path(args.file)
    if not json_path.exists():
        print(f"Filen hittades inte: {json_path}")
        sys.exit(1)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    tracks = data.get("tracks", [])
    print(f"Läser {len(tracks)} låtar från {json_path.name}")

    if args.dry_run:
        uid, models = None, None
        print("[DRY RUN — inga ändringar skrivs]")
    else:
        uid, models = connect()

    caches = {"work_type": {}, "genre": {}}
    counts = {"created": 0, "updated": 0}

    for track in tracks:
        result = upsert_song(models, uid, track, caches, args.dry_run)
        if result in counts:
            counts[result] += 1

    print(f"\nKlart: {counts['created']} skapade, {counts['updated']} uppdaterade")


if __name__ == "__main__":
    main()
