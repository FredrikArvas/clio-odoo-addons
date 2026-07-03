from odoo import fields, models


class SsfPersonChip(models.Model):
    _name        = "ssf.person.chip"
    _description = "Chip-kod (person)"
    _rec_name    = "chip_no"
    _order       = "partner_id, sector_id, chip_no"

    partner_id = fields.Many2one(
        "res.partner", string="Person",
        required=True, ondelete="cascade", index=True,
    )
    chip_no = fields.Char(string="Chip-nummer", required=True, index=True)
    sector_id = fields.Many2one(
        "ssf.sector", string="Gren",
        ondelete="set null",
    )
    ssfta_id = fields.Integer(string="SSFTA ID", readonly=True, index=True)
    source = fields.Selection(
        [("ssfta", "SSFTA"), ("manual", "Manuell")],
        string="Kalla", default="ssfta", readonly=True,
    )

    _chip_unique = models.Constraint(
        "UNIQUE(chip_no, sector_id)",
        "Chip-nummer + gren maste vara unikt.",
    )
