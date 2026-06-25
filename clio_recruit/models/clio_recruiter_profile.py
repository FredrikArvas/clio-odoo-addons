"""
clio_recruiter_profile.py
Rekryterarprofil för passiv kandidatsourcing.
En profil per rekryteringsuppdrag (t.ex. "CapFM SAP-rekrytering").
"""

import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ClioRecruiterProfile(models.Model):
    _name        = "clio.recruiter.profile"
    _description = "Clio Recruit — Rekryterarprofil"
    _order       = "name"
    _rec_name    = "name"

    name = fields.Char(
        string   = "Profilnamn",
        required = True,
        index    = True,
        help     = "Internt namn för uppdraget, t.ex. 'CapFM SAP-rekrytering'.",
    )
    partner_id = fields.Many2one(
        comodel_name = "res.partner",
        string       = "Mottagare",
        domain       = [("email", "!=", False)],
        help         = "Kontakt dit Clio skickar signalrapporter.",
    )
    email = fields.Char(
        string   = "Mottagaradress",
        compute  = "_compute_email",
        store    = True,
        readonly = True,
        help     = "Beräknat från partner_id.email — läses av agenten via XML-RPC.",
    )
    language = fields.Selection(
        selection = [("sv", "Svenska"), ("en", "English")],
        string    = "Rapportspråk",
        default   = "sv",
    )
    target_role = fields.Char(
        string = "Målroll",
        help   = "T.ex. 'Senior SAP-arkitekt / SAP-konsult'.",
    )
    target_seniority = fields.Selection(
        selection = [
            ("junior", "Junior (0–3 år)"),
            ("medel",  "Medel (4–6 år)"),
            ("senior", "Senior (6–12 år)"),
            ("expert", "Expert (12+ år)"),
        ],
        string = "Senioritetsnivå",
    )
    candidate_type_ids = fields.Many2many(
        comodel_name = "clio.recruiter.candidate.type",
        string       = "Kandidattyper",
        help         = "Vilka typer av kandidater profilen söker.",
    )
    target_characteristics = fields.Text(
        string = "Kandidatkaraktäristik",
        help   = "Egenskaper att leta efter — en per rad.",
    )
    target_avoid = fields.Text(
        string = "Undvik",
        help   = "Profiler att exkludera — en per rad.",
    )
    target_industries = fields.Text(
        string = "Målbranscher",
        help   = "Branscher att bevaka — en per rad.",
    )
    trigger_signals_high = fields.Text(
        string = "Högvärda signaler",
        help   = "Marknadshändelser med hög sannolikhet för kandidattillgång — en per rad.",
    )
    trigger_signals_medium = fields.Text(
        string = "Medelvärda signaler",
        help   = "Marknadshändelser att bevaka sekundärt — en per rad.",
    )
    confidential_client = fields.Boolean(
        string  = "Konfidentiell klient",
        default = True,
        help    = "Dölj klientnamn i utskickade rapporter.",
    )
    client_hint = fields.Char(
        string = "Klientbeskrivning",
        help   = "Hur klienten beskrivs i rapporter om konfidentiell, t.ex. 'ett ledande konsultbolag'.",
    )
    active = fields.Boolean(
        string  = "Aktiv",
        default = True,
    )
    match_ids = fields.One2many(
        comodel_name = "clio.recruiter.match",
        inverse_name = "profile_id",
        string       = "Matchhistorik",
    )
    match_count = fields.Integer(
        string  = "Matchningar",
        compute = "_compute_match_count",
        store   = False,
    )

    @api.depends("partner_id.email")
    def _compute_email(self):
        for rec in self:
            rec.email = rec.partner_id.email or ""

    def _compute_match_count(self):
        for rec in self:
            rec.match_count = len(rec.match_ids)

    def action_view_matches(self):
        self.ensure_one()
        return {
            "type":     "ir.actions.act_window",
            "name":     "Matchhistorik",
            "res_model": "clio.recruiter.match",
            "view_mode": "list,form",
            "domain":   [("profile_id", "=", self.id)],
            "context":  {"default_profile_id": self.id},
        }
