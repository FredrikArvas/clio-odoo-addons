from odoo import fields, models


class UapEncounter(models.Model):
    """Koppling encounter ↔ Larry Hatch U*-post (många-till-många)."""

    _inherit = "uap.encounter"

    larry_hatch_case_ids = fields.Many2many(
        comodel_name="afu.larry_hatch.case",
        relation="uap_encounter_larry_hatch_rel",
        column1="encounter_id",
        column2="case_id",
        string="Larry Hatch U*",
    )
    larry_hatch_count = fields.Integer(
        string="# Larry Hatch",
        compute="_compute_larry_hatch_count",
    )

    def _compute_larry_hatch_count(self):
        for rec in self:
            rec.larry_hatch_count = len(rec.larry_hatch_case_ids)

    def action_open_larry_hatch_cases(self):
        self.ensure_one()
        return {
            "type":      "ir.actions.act_window",
            "name":      "Larry Hatch U*",
            "res_model": "afu.larry_hatch.case",
            "view_mode": "list,form",
            "domain":    [("id", "in", self.larry_hatch_case_ids.ids)],
            "context":   {"create": False},
        }
