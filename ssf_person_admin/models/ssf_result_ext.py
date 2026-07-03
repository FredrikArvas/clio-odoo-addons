from odoo import fields, models


class SsfResultListSource(models.Model):
    _inherit = "ssf.result.list"

    source = fields.Selection(
        [("ssfta", "SSFTA"), ("ssftiming", "SSFTiming")],
        string="Kalla", default="ssfta",
    )


class SsfResultSource(models.Model):
    _inherit = "ssf.result"

    source = fields.Selection(
        [("ssfta", "SSFTA"), ("ssftiming", "SSFTiming")],
        string="Kalla", default="ssfta",
    )
