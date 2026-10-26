"""Import av begravningspsalmer från begravningspsalmer.json → clio.media.work (work_type=Psalm).

Upsert-nyckel: psalm_nr (primär, scheme "psalm_nr"), annars name.
Spotify-URL läggs bara till som identifierare för track-URL:er (inte playlists).
Kör: python import_psalms.py [--dry-run] [--file /annan/sökväg.json]
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
    "Dropbox/projekt/Clio-projekt/Clio_Reco/begravningspsalmer.json"
)

WORK_TYPE_NAME = "Psalm"
FIXED_GENRE = "Begravningspsalm"


def build_description(track: dict) -> str:
    parts = []
    if track.get("subtitle"):
        parts.append(f"<p><i>{track['subtitle']}</i></p>")
    if track.get("theme"):
        parts.append(f"<p><b>Tema:</b> {track['theme']}</p>")
    if track.get("mood"):
        parts.append(f"<p><b>Stämning:</b> {track['mood']}</p>")
    if track.get("begravning_rank"):
        parts.append(f"<p><b>Popularitet:</b> {track['begravning_rank']}</p>")
    if track.get("notes"):
        parts.append(f"<p>{track['notes']}</p>")
    return "".join(parts)


def _is_track_url(url: str) -> bool:
    return bool(url) and "/track/" in url


def _ensure_identifier(models, uid, work_id: int, scheme: str, value: str) -> None:
    """Lägger till identifierare om värdet inte redan finns (globalt, undviker UNIQUE-konflikt)."""
    existing = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "clio.media.work.identifier", "search",
        [[["scheme", "=", scheme], ["value", "=", value]]],
    )
    if not existing:
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "clio.media.work.identifier", "create",
            [{"work_id": work_id, "scheme": scheme, "value": value}],
        )
    elif existing and models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "clio.media.work.identifier", "read",
        [existing, ["work_id"]],
    )[0]["work_id"][0] != work_id:
        print(f"  [VARNING] {scheme}:{value[:50]} används redan av annat verk — hoppar över")


def upsert_psalm(models, uid, track: dict, caches: dict, dry_run: bool) -> str:
    psalm_nr = track.get("psalm_nr")
    title = track["title"].strip()
    name = f"{title} (nr {psalm_nr})" if psalm_nr else title
    spotify_url = (track.get("spotify_url") or "").strip()
    track_url = spotify_url if _is_track_url(spotify_url) else ""
    composer = (track.get("composer_text") or "").strip()

    if dry_run:
        existing = []
    elif psalm_nr:
        existing = find_work_by_identifier(models, uid, "psalm_nr", str(psalm_nr))
    else:
        existing = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "clio.media.work", "search",
            [[["name", "=", name], ["work_type_id.code", "=", "psalm"]]],
        )

    work_type_id = ensure_work_type(models, uid, WORK_TYPE_NAME, caches["work_type"]) if not dry_run else -1

    genre_names = [FIXED_GENRE]
    extra = (track.get("genre") or "").strip()
    if extra and extra != "Psalm":
        genre_names.append(extra)
    genre_ids = []
    for gname in genre_names:
        gid = ensure_genre(models, uid, gname, caches["genre"]) if not dry_run else -1
        if gid > 0:
            genre_ids.append((4, gid))

    vals = {
        "name": name,
        "work_type_id": work_type_id,
        "author": composer or False,
        "description": build_description(track),
        "genre_ids": genre_ids,
    }

    if dry_run:
        track_note = f" [track: {track_url[:40]}…]" if track_url else ""
        action = "UPDATE" if existing else "CREATE"
        print(f"  [{action}] {name}{track_note}")
        return action.lower()

    if existing:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "clio.media.work", "write", [existing, vals])
        action = "updated"
        work_id = existing[0]
    else:
        work_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "clio.media.work", "create", [vals])
        action = "created"

    if psalm_nr:
        _ensure_identifier(models, uid, work_id, "psalm_nr", str(psalm_nr))
    if track_url:
        _ensure_identifier(models, uid, work_id, "spotify", track_url)

    return action


def main():
    parser = argparse.ArgumentParser(description="Importera begravningspsalmer till clio.media.work")
    parser.add_argument("--dry-run", action="store_true", help="Simulera utan att skriva till Odoo")
    parser.add_argument("--file", default=str(DEFAULT_JSON), help="Sökväg till JSON-fil")
    args = parser.parse_args()

    json_path = Path(args.file)
    if not json_path.exists():
        print(f"Filen hittades inte: {json_path}")
        sys.exit(1)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    tracks = data.get("tracks", [])
    print(f"Läser {len(tracks)} psalmer från {json_path.name}")

    if args.dry_run:
        uid, models = None, None
        print("[DRY RUN — inga ändringar skrivs]")
    else:
        uid, models = connect()

    caches = {"work_type": {}, "genre": {}}
    counts = {"created": 0, "updated": 0}

    for track in tracks:
        result = upsert_psalm(models, uid, track, caches, args.dry_run)
        if result in counts:
            counts[result] += 1

    print(f"\nKlart: {counts['created']} skapade, {counts['updated']} uppdaterade")


if __name__ == "__main__":
    main()
