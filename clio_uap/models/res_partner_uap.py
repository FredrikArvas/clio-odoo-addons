from odoo import models, fields


class ResPartnerUap(models.Model):
    _inherit = "res.partner"

    uap_org_type = fields.Selection(
        selection=[
            ("ufo_org", "UFO / UAP Research Org"), ("govt", "Government / Military"),
            ("scientific", "Scientific / Academic"), ("civilian", "Civilian / Nonprofit"),
            ("lobby", "Policy / Lobby"), ("archive", "Archive / Library"),
        ],
        string="UAP Org Type",
        index=True,
    )
    uap_org_id         = fields.Char(string="UAP Org ID", index=True)
    uap_research_notes = fields.Text(string="UAP Research Notes")
    uap_database_ids   = fields.One2many("uap.database", "partner_id", string="UAP Databases")
    uap_database_count = fields.Integer(string="# Databases", compute="_compute_uap_database_count", store=False)

    # --- Kontaktregister-fält (från uap_sources CSV) ---
    uap_contact_type = fields.Selection(
        selection=[("person", "Person"), ("organization", "Organisation"), ("anonymous", "Anonym")],
        string="UAP Contact Type",
        index=True,
    )
    uap_role          = fields.Char(string="UAP Role", help="journalist, researcher, whistleblower, pilot, official ...")
    uap_credibility   = fields.Selection(
        selection=[("1", "Tier 1 — Hög"), ("2", "Tier 2 — Medel"), ("3", "Tier 3 — Låg/Anonym")],
        string="Credibility Tier",
        index=True,
    )
    uap_focus_areas   = fields.Char(string="Focus Areas", help="Semikolon-separerat: aerial;disclosure;military")
    uap_language      = fields.Char(string="Primary Language(s)", help="en, sv, fr ...")
    uap_social_media  = fields.Char(string="Social Media Handle")
    uap_podcast_name  = fields.Char(string="Podcast Name")
    uap_rss_feed      = fields.Char(string="RSS Feed URL")

    def _compute_uap_database_count(self):
        for rec in self:
            rec.uap_database_count = len(rec.uap_database_ids)
