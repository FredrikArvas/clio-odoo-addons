import json
import logging
import re
import uuid

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class GsfJubileumFastighet(models.Model):
    _name = "gsf.jubileum.fastighet"
    _description = "GSF Jubileum — Berättelse"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "namn"
    _rec_name = "namn"

    _unik_token_unique = models.Constraint(
        "UNIQUE(unik_token)",
        "Token måste vara unikt per fastighet.",
    )

    property_id = fields.Many2one(
        "property.property",
        string="Fastighet",
        required=True,
        ondelete="restrict",
        index=True,
    )
    namn = fields.Char(
        string="Visningsnamn",
        compute="_compute_namn",
        store=True,
        readonly=False,
        index=True,
        help="Hämtas från fastighetens beteckning, kan skrivas över manuellt.",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Kontaktperson",
        ondelete="set null",
    )
    email = fields.Char(
        string="E-post",
        compute="_compute_email",
        store=True,
        readonly=False,
        help="Hämtas från kontaktpersonen, kan skrivas över manuellt.",
    )
    unik_token = fields.Char(
        string="Token",
        default=lambda self: str(uuid.uuid4()),
        index=True,
        copy=False,
        readonly=True,
        help="UUID som används i chatt-länken. Genereras automatiskt.",
    )
    status = fields.Selection(
        [
            ("ej_kontaktad",            "Ej kontaktad"),
            ("inbjuden",                "Inbjuden"),
            ("paborjad",                "Påbörjad"),
            ("inlamnad",                "Inlämnad"),
            ("vantar_godkannande",      "Väntar godkännande"),
            ("godkand_for_publicering", "Godkänd för publicering"),
            ("vill_ej_publiceras",      "Vill ej publiceras"),
        ],
        string="Status",
        default="ej_kontaktad",
        required=True,
        index=True,
        tracking=True,
    )
    kanal = fields.Selection(
        [
            ("skriftligt",  "Skriftligt (mejl)"),
            ("samtal",      "Samtal med Fredrik"),
            ("clio_chatt",  "Clio-chatt (webbgränssnitt)"),
            ("ej_valt",     "Ej valt"),
        ],
        string="Kanal",
        default="ej_valt",
        tracking=True,
    )
    datum_inbjudan = fields.Date(string="Datum — inbjudan", copy=False)
    datum_inlamnad = fields.Date(string="Datum — inlämnad", copy=False)
    coaching_history = fields.Text(
        string="Chatthistorik (JSON)",
        copy=False,
        help="JSON-array [{role, content}] — sparas löpande under Clio-chatten.",
    )
    anteckningar = fields.Text(
        string="Redaktörens anteckningar",
        help="Interna redaktörsnotat, syns ej för familjen.",
    )
    chatt_url = fields.Char(
        string="Länk till besökarformuläret",
        compute="_compute_chatt_url",
    )
    lasvy_url = fields.Char(
        string="Läsvy (redaktör)",
        compute="_compute_chatt_url",
    )
    svar_ids = fields.One2many("gsf.jubileum.svar", "fastighet_id", string="Svar")
    samtycke_ids = fields.One2many("gsf.jubileum.samtycke", "fastighet_id", string="Samtycke")

    @api.depends("property_id", "property_id.code", "property_id.name")
    def _compute_namn(self):
        for rec in self:
            p = rec.property_id
            if p:
                rec.namn = p.code or p.name or ""
            elif not rec.namn:
                rec.namn = ""

    def _compute_chatt_url(self):
        base = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "")
        for rec in self:
            rec.chatt_url = f"{base}/jubileum/{rec.unik_token}" if rec.unik_token else ""
            rec.lasvy_url = f"{base}/jubileum/{rec.unik_token}/lasvy" if rec.unik_token else ""

    @api.depends("partner_id", "partner_id.email")
    def _compute_email(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.email:
                rec.email = rec.partner_id.email

    def action_generera_token(self):
        self.ensure_one()
        self.unik_token = str(uuid.uuid4())

    def action_kopiera_chattlank(self):
        self.ensure_one()
        url = self.chatt_url
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Chatt-länk",
                "message": url,
                "type": "info",
                "sticky": True,
            },
        }

    def action_skicka_inbjudan(self):
        template = self.env.ref("gsf_jubileum.mail_template_jubileum_inbjudan")
        for rec in self:
            if not rec.email:
                rec.message_post(
                    body="⚠️ Ingen e-postadress registrerad — inbjudan ej skickad.",
                    message_type="comment",
                    subtype_xmlid="mail.mt_note",
                )
                continue
            template.send_mail(rec.id, force_send=True)
            if rec.status == "ej_kontaktad":
                rec.write({
                    "status": "inbjuden",
                    "datum_inbjudan": fields.Date.today(),
                })
            rec.message_post(
                body=f"📧 Inbjudan skickad till {rec.email}.",
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )

    @api.model
    def skicka_lank_for_email(self, email):
        email = (email or "").strip().lower()
        if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            return
        # Escapa LIKE-wildcards — annars kan t.ex. "%" matcha alla poster
        pattern = email.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        records = self.search([
            ("email", "=ilike", pattern),
            ("status", "not in", ["vill_ej_publiceras"]),
        ])
        if not records:
            return
        template = self.env.ref("gsf_jubileum.mail_template_jubileum_inbjudan")
        for rec in records:
            template.send_mail(rec.id, force_send=True)

    def action_markera_inbjuden(self):
        for rec in self:
            if rec.status == "ej_kontaktad":
                rec.write({"status": "inbjuden", "datum_inbjudan": fields.Date.today()})

    @api.model
    def chat_history_parsed(self, fastighet_id):
        rec = self.browse(fastighet_id)
        return json.loads(rec.coaching_history or "[]")

    def action_reextract_svar(self):
        import requests as _requests
        from ..fragor import FRAGOR

        self.ensure_one()
        history = json.loads(self.coaching_history or "[]")
        if not history:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Ingen historik",
                    "message": "Chatthistoriken är tom, inget att bearbeta.",
                    "type": "warning",
                },
            }

        icp = self.env["ir.config_parameter"].sudo()
        url = icp.get_param("gsf.bridge.url", "http://172.19.0.1:8090")
        secret = icp.get_param("gsf.bridge.secret")
        if not secret:
            raise ValueError("gsf.bridge.secret saknas i Odoo-konfigurationen")

        try:
            resp = _requests.post(
                f"{url}/extract",
                json={
                    "fastighet_token": self.unik_token,
                    "history": history,
                    "fragor": FRAGOR,
                },
                headers={"X-Bridge-Secret": secret},
                timeout=60,
            )
            resp.raise_for_status()
            svar_map = resp.json().get("svar")
        except Exception as exc:
            _logger.error("reextract bridge call failed for %s: %s", self.id, exc)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Bridge-fel",
                    "message": f"Kunde inte nå AI-tjänsten: {exc}",
                    "type": "danger",
                },
            }

        if not svar_map:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Extraktion misslyckades",
                    "message": "AI returnerade inga svar. Försök igen.",
                    "type": "warning",
                },
            }

        self.svar_ids.unlink()
        SvarModel = self.env["gsf.jubileum.svar"].sudo()
        for nr, rubrik, fraga_text in FRAGOR:
            SvarModel.create({
                "fastighet_id": self.id,
                "fraga_nr": str(nr),
                "fraga_text": fraga_text,
                "svar_text": svar_map.get(str(nr), "") or "",
                "kalla": "clio_chatt",
            })
        n = len(FRAGOR)
        self.message_post(
            body=f"Svar ombearbetade: {n} svarsposter återskapade från chatthistorik.",
            message_type="comment",
            subtype_xmlid="mail.mt_note",
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Klart",
                "message": f"{n} svarsposter återskapade.",
                "type": "success",
            },
        }

    def action_skicka_bekraftelse(self):
        self.ensure_one()
        if not self.email:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {"title": "Ingen e-post", "message": "Fastigheten saknar e-postadress.", "type": "warning"},
            }
        template = self.env.ref("gsf_jubileum.mail_template_jubileum_bekraftelse")
        template.send_mail(self.id, force_send=True)
        self.message_post(
            body=f"Intervjusammanfattning skickad manuellt till {self.email}.",
            message_type="comment",
            subtype_xmlid="mail.mt_note",
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {"title": "Skickat", "message": f"Mail skickat till {self.email}.", "type": "success"},
        }
