"""
clio_recruiter_match.py
En matchningspost per signalartikel per rekryterarprofil.
Skapas av clio-recruiter när en artikel når matchtröskel och rapport skickats.
"""

from odoo import fields, models


class ClioRecruiterMatch(models.Model):
    _name        = "clio.recruiter.match"
    _description = "Clio Recruit — Matchad signal"
    _order       = "sent_at desc"
    _rec_name    = "article_id"

    profile_id = fields.Many2one(
        comodel_name = "clio.recruiter.profile",
        string       = "Rekryterarprofil",
        required     = True,
        ondelete     = "cascade",
        index        = True,
    )
    article_id = fields.Many2one(
        comodel_name = "clio.media.article",
        string       = "Artikel",
        ondelete     = "set null",
        index        = True,
    )
    target_company = fields.Char(
        string = "Bolag (text)",
        index  = True,
        help   = "Bolagsnamn skrivet av agenten via XML-RPC.",
    )
    company_id = fields.Many2one(
        comodel_name = "res.partner",
        string       = "Bolag",
        domain       = [("is_company", "=", True)],
        index        = True,
        help         = "Länk till Odoo-kontakt. Sätts manuellt.",
    )
    candidate_profile = fields.Char(
        string = "Kandidatbeskrivning",
        help   = "Fritextbeskrivning av kandidattyp skriven av agenten.",
    )
    candidate_type_ids = fields.Many2many(
        comodel_name = "clio.recruiter.candidate.type",
        string       = "Kandidattyper",
        help         = "Välj en eller flera kandidattyper.",
    )
    signal_type = fields.Selection(
        selection = [
            ("outsourcing",      "Outsourcing"),
            ("varsel",           "Varsel"),
            ("s4hana_migration", "S/4HANA-migration"),
            ("cio_byte",         "CIO-byte"),
            ("artikel_generell", "Artikel (generell)"),
        ],
        string = "Signaltyp",
    )
    match_score = fields.Integer(
        string = "Score",
        help   = "0–100 från AI-analysen.",
    )
    estimated_timeline = fields.Char(
        string = "Tidshorisont",
        help   = "Uppskattad tid tills kandidater kan bli tillgängliga, t.ex. '3–6 månader'.",
    )
    contact_hint = fields.Char(
        string = "Kontakttips",
        help   = "Rekommenderat sätt att nå potentiella kandidater.",
    )
    recommended_action = fields.Char(
        string = "Rekommenderad åtgärd",
        help   = "T.ex. kontakta_nu, bevaka_3_mån, skip.",
    )
    sent_at = fields.Datetime(
        string = "Rapport skickad",
        index  = True,
        help   = "Tidsstämpel för när rapporten skickades.",
    )
