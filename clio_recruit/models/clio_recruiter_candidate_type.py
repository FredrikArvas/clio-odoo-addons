from odoo import models, fields


class ClioRecruiterCandidateType(models.Model):
    _name        = "clio.recruiter.candidate.type"
    _description = "Clio Recruit — Kandidattyp"
    _order       = "sequence, name"

    name     = fields.Char(string="Kandidattyp", required=True, translate=True)
    sequence = fields.Integer(default=10)
