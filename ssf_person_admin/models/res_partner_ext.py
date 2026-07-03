from odoo import fields, models


class ResPartnerPersonAdmin(models.Model):
    _inherit = "res.partner"

    fis_code = fields.Char(
        string="FIS-kod",
        index=True,
        help="Personens primara FIS-kod.",
    )
    chip_ids = fields.One2many(
        "ssf.person.chip", "partner_id", string="Chip-koder",
    )
