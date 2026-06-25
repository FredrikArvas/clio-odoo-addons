from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    clio_recruit_profile_ids = fields.One2many(
        comodel_name = "clio.recruiter.profile",
        inverse_name = "partner_id",
        string       = "Clio Recruit",
    )
