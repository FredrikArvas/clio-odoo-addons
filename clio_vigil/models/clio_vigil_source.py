"""
clio_vigil_source.py
Bevakningskällor: RSS-flöden, YouTube-kanaler, Google News-frågor och webbsajter.
Kanonisk källa för pipeline-konfiguration — ersätter YAML-källlistor.
"""

from __future__ import annotations

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ClioVigilSource(models.Model):
    _name        = "clio.vigil.source"
    _description = "Clio Vigil — Bevakningskälla"
    _order       = "domain, source_type, name"
    _rec_name    = "name"

    name = fields.Char(
        string   = "Namn",
        required = True,
        index    = True,
    )
    domain = fields.Selection(
        selection = [("ufo", "UFO/UAP"), ("ai", "AI-modeller")],
        string    = "Domän",
        required  = True,
        index     = True,
    )
    source_type = fields.Selection(
        selection = [
            ("rss",          "RSS"),
            ("youtube",      "YouTube"),
            ("google_news",  "Google News"),
            ("web",          "Webb"),
        ],
        string   = "Typ",
        required = True,
    )
    url = fields.Char(
        string = "URL",
        index  = True,
        help   = "Feed-URL (RSS/webb) eller kanal-URL (YouTube). "
                 "Inte obligatorisk för Google News — använd Sökfras istället.",
    )

    # ── YouTube-specifikt ────────────────────────────────────────────────────
    channel_id = fields.Char(
        string = "Kanal-ID / Handle",
        help   = "YouTube @handle eller UC-kanal-ID (t.ex. '@theblackvault'). "
                 "Pipeline bygger kanal-URL automatiskt från detta värde.",
    )

    # ── Google News-specifikt ────────────────────────────────────────────────
    google_news_query = fields.Char(
        string = "Sökfras",
        help   = "Sökfras för Google News RSS (t.ex. 'UAP disclosure'). "
                 "Används när Typ = Google News.",
    )
    lang = fields.Char(
        string  = "Språk",
        default = "en",
        help    = "ISO 639-1 (en, sv). Används för Google News.",
    )
    country = fields.Char(
        string  = "Land",
        default = "US",
        help    = "ISO 3166-1 alpha-2 (US, SE). Används för Google News.",
    )

    # ── Prioritet och kvalitet ───────────────────────────────────────────────
    maturity = fields.Selection(
        selection = [
            ("tidig",     "Tidig källa"),
            ("etablerad", "Etablerad"),
            ("akademisk", "Akademisk"),
        ],
        string  = "Mognad",
        default = "tidig",
        help    = "Källkvalitet — metadata, blockerar aldrig insamling.",
    )
    weight = fields.Float(
        string  = "Vikt",
        default = 1.0,
        help    = "Prioritetsmultiplikator (standard 1.0, högt förtroende 1.2+).",
    )
    transcription_threshold = fields.Float(
        string = "Transkriptionströskel",
        digits = (3, 2),
        help   = "Relevanströskel för transkription (0.0–1.0). "
                 "Tomt (0.0) = använd domänstandard från YAML.",
    )

    # ── Autentisering ────────────────────────────────────────────────────────
    auth_env = fields.Char(
        string = "Auth-miljövariabel",
        help   = "Namn på miljövariabel med inloggning (format USER:PASSWORD). "
                 "T.ex. FOKUS_RSS_AUTH. Värdet läses från serverns .env-fil.",
    )

    # ── Övrigt ───────────────────────────────────────────────────────────────
    active = fields.Boolean(
        string  = "Aktiv",
        default = True,
    )
    archive_enabled = fields.Boolean(
        string  = "Arkivera lokalt",
        default = False,
        help    = "Om aktiverad laddar --archive-sources ned hela källarkivet.",
    )
    notes = fields.Text(string="Anteckningar")

    # ── Validering ───────────────────────────────────────────────────────────
    @api.constrains("source_type", "url", "channel_id", "google_news_query")
    def _check_required_by_type(self):
        for rec in self:
            if rec.source_type == "rss" and not rec.url:
                raise models.ValidationError(
                    f"RSS-källa '{rec.name}' kräver en URL."
                )
            if rec.source_type == "youtube" and not rec.channel_id:
                raise models.ValidationError(
                    f"YouTube-källa '{rec.name}' kräver Kanal-ID / Handle."
                )
            if rec.source_type == "google_news" and not rec.google_news_query:
                raise models.ValidationError(
                    f"Google News-källa '{rec.name}' kräver en Sökfras."
                )

    _name_domain_uniq = models.Constraint(
        "UNIQUE(domain, name)",
        "Källnamnet måste vara unikt inom domänen.",
    )
