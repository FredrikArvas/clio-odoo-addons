"""
clio_recruiter_profile.py
Rekryterarprofil för passiv kandidatsourcing.
En profil per rekryteringsuppdrag (t.ex. "CapFM SAP-rekrytering").
"""

import json
import logging
import urllib.error
import urllib.request

from markupsafe import Markup
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ClioRecruiterProfile(models.Model):
    _name        = "clio.recruiter.profile"
    _description = "Clio Recruit — Rekryterarprofil"
    _order       = "name"
    _rec_name    = "name"
    _inherit     = ["mail.thread", "mail.activity.mixin"]

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

    def action_run_manual_search(self):
        self.ensure_one()
        if not self.email:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {"message": "Profilen saknar mottagaradress.", "type": "warning"},
            }
        base = self.env["ir.config_parameter"].sudo().get_param(
            "clio.service.url", default="http://172.19.0.1:7200"
        )
        url = base.rstrip("/") + "/recruit/run"
        body = json.dumps({"profile_id": self.id}).encode()
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=310) as resp:
                result = json.loads(resp.read())
        except urllib.error.URLError as exc:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {"message": f"Kunde inte nå clio-service: {exc.reason}", "type": "danger"},
            }
        except Exception as exc:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {"message": f"Sökning misslyckades: {exc}", "type": "danger"},
            }
        if not result.get("ok"):
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {"message": result.get("error", "Okänt fel från clio-service"), "type": "danger"},
            }
        output = result.get("output", "")
        self.message_post(
            body=Markup("<b>Manuell sökning</b><br/><pre>{}</pre>").format(output[:4000]),
            subject=f"Manuell sökning — {self.name}",
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {"message": "Sökning klar — se chatter för resultat.", "type": "success"},
        }

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
