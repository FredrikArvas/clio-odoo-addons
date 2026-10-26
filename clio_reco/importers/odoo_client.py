"""Delad XML-RPC-anslutning till Odoo. Läs credentials från .env."""
import os
import xmlrpc.client
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

ODOO_URL = os.environ["ODOO_URL"]
ODOO_DB = os.environ["ODOO_DB"]
ODOO_USER = os.environ["ODOO_USER"]
ODOO_PASSWORD = os.environ["ODOO_PASSWORD"]


def connect():
    """Returnerar (uid, models-proxy) redo för execute_kw-anrop."""
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    if not uid:
        raise RuntimeError(f"Inloggning misslyckades: {ODOO_USER}@{ODOO_URL} ({ODOO_DB})")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    return uid, models


def ensure_work_type(models, uid, name: str, _cache: dict) -> int:
    """Hämtar clio.media.work.type-ID för givet namn (cachat)."""
    if name in _cache:
        return _cache[name]
    ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "clio.media.work.type", "search",
        [[["name", "=", name]]],
    )
    if not ids:
        raise ValueError(f"Verkstyp saknas i Odoo: '{name}'")
    _cache[name] = ids[0]
    return ids[0]


def ensure_genre(models, uid, name: str, _cache: dict) -> int:
    """Hämtar eller skapar en clio.media.genre och returnerar dess ID (cachat)."""
    if name in _cache:
        return _cache[name]
    existing = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "clio.media.genre", "search",
        [[["name", "=", name]]],
    )
    if existing:
        _cache[name] = existing[0]
    else:
        _cache[name] = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "clio.media.genre", "create",
            [{"name": name}],
        )
    return _cache[name]


def find_work_by_identifier(models, uid, scheme: str, value: str) -> list[int]:
    """Returnerar work-ID:n som har en matchande identifierare."""
    ident_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "clio.media.work.identifier", "search",
        [[["scheme", "=", scheme], ["value", "=", value]]],
    )
    if not ident_ids:
        return []
    records = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "clio.media.work.identifier", "read",
        [ident_ids, ["work_id"]],
    )
    return [r["work_id"][0] for r in records if r.get("work_id")]
