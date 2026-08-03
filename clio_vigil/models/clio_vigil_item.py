"""
clio_vigil_item.py
Pipeline-objekt: artiklar, podcastavsnitt och YouTube-klipp som passerar
genom clio-vigils bearbetningskedja (filter → transkription → RAG → digest).
Speglar vigil_items-tabellen i SQLite.
"""

from __future__ import annotations

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ClioVigilItem(models.Model):
    _name        = "clio.vigil.item"
    _description = "Clio Vigil — Bevakningsobjekt"
    _order       = "priority_score desc, published_at desc"
    _rec_name    = "title"

    # ── Identifiering ────────────────────────────────────────────────────────

    url = fields.Char(
        string   = "URL",
        required = True,
        index    = True,
        copy     = False,
    )
    title = fields.Char(string="Titel")

    # ── Källmetadata ─────────────────────────────────────────────────────────

    domain = fields.Selection(
        selection = [("ufo", "UFO/UAP"), ("ai", "AI-modeller")],
        string    = "Domän",
        index     = True,
    )
    source_type = fields.Selection(
        selection = [("rss", "RSS"), ("youtube", "YouTube / Facebook"), ("web", "Webb"), ("google_news", "Google News")],
        string    = "Källtyp",
    )
    source_name = fields.Char(string="Källa", index=True)
    source_maturity = fields.Selection(
        selection = [
            ("tidig",     "Tidig källa"),
            ("etablerad", "Etablerad"),
            ("akademisk", "Akademisk"),
        ],
        string = "Mognad",
    )
    published_at = fields.Datetime(
        string = "Publicerat",
        index  = True,
    )
    duration_seconds = fields.Integer(
        string = "Längd (s)",
        help   = "Längd i sekunder. Tomt för webb/PDF.",
    )

    # ── Poäng och prioritet ──────────────────────────────────────────────────

    relevance_score = fields.Float(
        string = "Relevansscore",
        digits = (5, 4),
        help   = "0.0–1.0 från nyckelordsfiltret.",
    )
    priority_score = fields.Float(
        string = "Prioritet",
        digits = (5, 4),
        index  = True,
        help   = "Relevansscore × källvikt × längdfaktor × tidsfaktor.",
    )

    # ── Tillstånd ────────────────────────────────────────────────────────────

    state = fields.Selection(
        selection = [
            ("discovered",  "Hittad"),
            ("filtered_in", "Passerade filter"),
            ("filtered_out","Filtrerades bort"),
            ("queued",      "I kö"),
            ("downloaded",  "Audio nedladdad"),
            ("transcribing","Transkriberas"),
            ("transcribed", "Transkriberad"),
            ("captioned",   "Auto-textad (YouTube)"),  # Sprint B
            ("summarized",  "Summerad"),
            ("uap_classified", "UAP-klassificerad"),
            ("indexed",     "Indexerad"),
            ("notified",    "Skickad i digest"),
            ("failed",      "Misslyckad"),
        ],
        string  = "Tillstånd",
        default = "discovered",
        index   = True,
    )

    # ── Innehåll ─────────────────────────────────────────────────────────────

    summary = fields.Text(
        string = "Sammanfattning",
        help   = "2–3 meningar från Claude API.",
    )
    transcript_snippet = fields.Text(
        string = "Transkript (utdrag)",
        help   = "Första 500 tecken av transkriptionen.",
    )
    error_message = fields.Text(
        string   = "Felmeddelande",
        readonly = True,
        help     = "Undantaget som fick pipelinen att sätta state=crashed.",
    )

    # ── Audio ────────────────────────────────────────────────────────────────

    audio_path = fields.Char(
        string = "Audio-sökväg",
        help   = "Absolut sökväg till audio-filen på servern (sätts av downloader).",
    )

    # ── Sprint C: Arkivering ─────────────────────────────────────────────────

    archive_downloaded = fields.Boolean(
        string  = "Arkiverad",
        default = False,
        help    = "Episoden finns nedladdad lokalt på servern.",
    )
    archive_path = fields.Char(
        string = "Arkivsökväg",
        help   = "Absolut sökväg till arkiverad fil på servern.",
    )

    # ── Tidsstämplar ─────────────────────────────────────────────────────────

    created_at  = fields.Datetime(string="Skapad",       copy=False)
    notified_at = fields.Datetime(string="Notifierad",   copy=False)

    media_article_ids = fields.One2many(
        comodel_name = "clio.media.article",
        inverse_name = "vigil_item_id",
        string       = "Mediaposter",
    )
    has_media_article = fields.Boolean(
        string  = "Har mediapost",
        compute = "_compute_has_media_article",
        store   = True,
    )

    @api.depends("media_article_ids")
    def _compute_has_media_article(self):
        for rec in self:
            rec.has_media_article = bool(rec.media_article_ids)

    _url_uniq = models.Constraint(
        "UNIQUE(url)",
        "Objekt-URL måste vara unik.",
    )

    # ── Åtgärder ─────────────────────────────────────────────────────────────

    def action_boost(self):
        """Boostar objektet till toppen av alla köer (prio 999).

        State-logik:
        - discovered / filtered_out / filtered_in / crashed → queued  (börja om från download-kön)
        - queued / downloaded / transcribing / transcribed /
          captioned / uap_classified / indexed / notified → behåll state, höj bara prio

        Manuellt skapade poster kräver domain + source_type för att pipelinen ska kunna
        importera dem till SQLite. Visar ett varningsmeddelande om dessa saknas.
        """
        self.ensure_one()

        missing = []
        if not self.domain:
            missing.append("Domän")
        if not self.source_type:
            missing.append("Källtyp")
        if missing:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Fält saknas",
                    "message": f"Sätt {' och '.join(missing)} innan du boostar — pipelinen behöver dem för att importera posten.",
                    "type": "warning",
                    "sticky": True,
                },
            }

        early_states = {"discovered", "filtered_out", "filtered_in", "crashed"}
        new_state = "queued" if self.state in early_states else self.state
        self.write({
            "priority_score": 999.0,
            "state": new_state,
        })
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Boostade!",
                "message": f"'{self.title or self.url[:60]}' boostad till toppen av kön (state: {new_state}).",
                "type": "success",
                "sticky": False,
            },
        }

    def action_reset_to_discovered(self):
        """Återställer objektet till discovered (börja om)."""
        self.ensure_one()
        self.write({
            "state": "discovered",
            "priority_score": 0.0,
        })
