from odoo import fields, models


class GsfJubileumSamtycke(models.Model):
    _name = "gsf.jubileum.samtycke"
    _description = "GSF Jubileum — Samtycke"
    _order = "tidsstampel desc"

    fastighet_id = fields.Many2one(
        "gsf.jubileum.fastighet",
        string="Fastighet",
        required=True,
        ondelete="cascade",
        index=True,
    )
    godkand_publicering = fields.Boolean(
        string="Godkänner publicering",
        default=False,
    )
    vill_bli_kontaktad_igen = fields.Boolean(
        string="Vill bli kontaktad igen",
        default=False,
    )
    kommentar = fields.Text(
        string="Kommentar / villkor",
        help="T.ex. 'publicera men inte mitt fullständiga namn'.",
    )
    tidsstampel = fields.Datetime(
        string="Tidsstämpel",
        default=fields.Datetime.now,
        copy=False,
    )
