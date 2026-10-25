from odoo import fields, models


class ClioMediaGenre(models.Model):
    _name = "clio.media.genre"
    _description = "Clio Media — Genre"
    _order = "name"

    name = fields.Char(string="Genre", required=True, translate=True)
    color = fields.Integer(string="Färg", default=0)
