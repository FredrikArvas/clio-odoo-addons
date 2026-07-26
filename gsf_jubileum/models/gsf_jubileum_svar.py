from odoo import fields, models


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
    fraga_nr = fields.Integer(string="Fråga nr", help="1–10 enligt frågelistan.")
    fraga_text = fields.Char(
        string="Frågans lydelse",
        help="Sparas för spårbarhet om frågelistan ändras.",
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
