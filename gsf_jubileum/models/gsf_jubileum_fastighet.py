import json
import logging
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
    kontakt_id = fields.Many2one(
        "res.partner",
        string="Kontaktperson",
        ondelete="set null",
    )
    epost = fields.Char(
        string="E-post",
        compute="_compute_epost",
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
    svar_ids = fields.One2many("gsf.jubileum.svar", "fastighet_id", string="Svar")
    samtycke_id = fields.One2many("gsf.jubileum.samtycke", "fastighet_id", string="Samtycke")

    @api.depends("property_id")
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

    @api.depends("kontakt_id")
    def _compute_epost(self):
        for rec in self:
            if rec.kontakt_id and rec.kontakt_id.email:
                rec.epost = rec.kontakt_id.email

    def action_generera_token(self):
        self.ensure_one()
        self.unik_token = str(uuid.uuid4())

    def action_kopiera_chattlank(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "")
        url = f"{base_url}/jubileum/{self.unik_token}"
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
            if not rec.epost:
                rec.message_post(body="⚠️ Ingen e-postadress registrerad — inbjudan ej skickad.")
                continue
            template.send_mail(rec.id, force_send=True)
            if rec.status == "ej_kontaktad":
                rec.write({
                    "status": "inbjuden",
                    "datum_inbjudan": fields.Date.today(),
                })
            rec.message_post(body=f"📧 Inbjudan skickad till {rec.epost}.")

    @api.model
    def skicka_lank_for_email(self, email):
        email = (email or "").strip().lower()
        if not email:
            return
        records = self.search([
            ("epost", "ilike", email),
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
