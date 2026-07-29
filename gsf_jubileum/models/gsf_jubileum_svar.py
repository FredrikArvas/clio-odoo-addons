from odoo import api, fields, models

from ..fragor import FRAGOR

_FRAGA_SELECTION = [(str(nr), f"{nr}. {rubrik}") for nr, rubrik, _ in FRAGOR]
_FRAGA_TEXT_MAP  = {nr: text for nr, _, text in FRAGOR}


class GsfJubileumSvar(models.Model):
    _name = "gsf.jubileum.svar"
    _description = "GSF Jubileum — Svar per fråga"
    _order = "fastighet_id, fraga_nr"

    fastighet_id = fields.Many2one(
        "gsf.jubileum.fastighet",
        string="Fastighet",
        required=True,
        ondelete="cascade",
        index=True,
    )
    fraga_nr = fields.Selection(
        _FRAGA_SELECTION,
        string="Fråga",
    )
    fraga_text = fields.Char(
        string="Frågans lydelse",
        help="Fylls i automatiskt när du väljer fråga.",
    )
    svar_text = fields.Text(string="Svar")
    kalla = fields.Selection(
        [
            ("clio_chatt",         "Clio-chatt"),
            ("mejl",               "Mejl"),
            ("samtalsanteckning",  "Samtalsanteckning"),
        ],
        string="Källa",
    )

    @api.onchange("fraga_nr")
    def _onchange_fraga_nr(self):
        if self.fraga_nr:
            self.fraga_text = _FRAGA_TEXT_MAP.get(int(self.fraga_nr), "")
