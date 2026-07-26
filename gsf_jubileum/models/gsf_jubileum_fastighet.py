import json
import logging
import uuid

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def _default_token():
    return str(uuid.uuid4())


class GsfJubileumFastighet(models.Model):
    _name = "gsf.jubileum.fastighet"
    _description = "GSF Jubileum — Fastighet"
    _order = "namn"
    _rec_name = "namn"

    _sql_constraints = [
        ("unik_token_unique", "UNIQUE(unik_token)", "Token måste vara unikt per fastighet."),
    ]

    namn = fields.Char(string="Fastighet/adress", required=True, index=True)
    kontakt_id = fields.Many2one(
        "res.partner",
        string="Kontaktperson",
        ondelete="set null",
        domain="[('category_id.name', '=', 'GSF:Agare')]",
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
        default=_default_token,
        index=True,
        copy=False,
        readonly=True,
        help="UUID som används i chatt-länken. Genereras automatiskt.",
    )
    status = fields.Selection(
        [
            ("ej_kontaktad",           "Ej kontaktad"),
            ("inbjuden",               "Inbjuden"),
            ("paborjad",               "Påbörjad"),
            ("inlamnad",               "Inlämnad"),
            ("vantar_godkannande",     "Väntar godkännande"),
            ("godkand_for_publicering","Godkänd för publicering"),
            ("vill_ej_publiceras",     "Vill ej publiceras"),
        ],
        string="Status",
        default="ej_kontaktad",
        required=True,
        index=True,
    )
    kanal = fields.Selection(
        [
            ("skriftligt",         "Skriftligt (mejl)"),
            ("samtal",             "Samtal med Fredrik"),
            ("clio_chatt",         "Clio-chatt (webbgränssnitt)"),
            ("ej_valt",            "Ej valt"),
        ],
        string="Kanal",
        default="ej_valt",
    )
    datum_inbjudan = fields.Date(string="Datum — inbjudan", copy=False)
    datum_inlamnad = fields.Date(string="Datum — inlämnad", copy=False)
    coaching_history = fields.Text(
        string="Chatthistorik (JSON)",
        copy=False,
        help="JSON-array [{role, content}] — sparas löpande under Clio-chatten.",
    )
    anteckningar = fields.Text(
        string="Fredriks anteckningar",
        help="Interna redaktörsnotat, syns ej för familjen.",
    )

    svar_ids = fields.One2many("gsf.jubileum.svar", "fastighet_id", string="Svar")
    samtycke_id = fields.One2many("gsf.jubileum.samtycke", "fastighet_id", string="Samtycke")

    @api.depends("kontakt_id")
    def _compute_epost(self):
        for rec in self:
            if rec.kontakt_id and rec.kontakt_id.email:
                rec.epost = rec.kontakt_id.email

    def action_generera_token(self):
        self.ensure_one()
        self.unik_token = _default_token()

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

    def action_markera_inbjuden(self):
        for rec in self:
            if rec.status == "ej_kontaktad":
                rec.write({"status": "inbjuden", "datum_inbjudan": fields.Date.today()})

    @api.model
    def chat_history_parsed(self, fastighet_id):
        rec = self.browse(fastighet_id)
        return json.loads(rec.coaching_history or "[]")
