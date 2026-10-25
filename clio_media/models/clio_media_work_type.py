from odoo import fields, models


class ClioMediaWorkType(models.Model):
    _name = "clio.media.work.type"
    _description = "Clio Media — Verkstyp"
    _order = "sequence, name"

    code = fields.Char(
        string="Kod",
        required=True,
        translate=False,
        help="Intern nyckel — ändras aldrig efter seed (kod litar på den).",
    )
    name = fields.Char(string="Namn", required=True, translate=True)
    sequence = fields.Integer(string="Ordning", default=10)
    active = fields.Boolean(string="Aktiv", default=True)

    _unique_code = models.Constraint(
        "UNIQUE(code)",
        "Verkstyskoden måste vara unik.",
    )
