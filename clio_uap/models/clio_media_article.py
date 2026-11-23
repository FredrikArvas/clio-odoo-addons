from odoo import fields, models


class ClioMediaArticleUap(models.Model):
    """UAP-tillägg på artikeln: klassificeringsmetod och koppling till encounters.
    relevance_class-fältet ägs av clio_media."""

    _inherit = "clio.media.article"

    encounter_ids = fields.Many2many(
        comodel_name="uap.encounter",
        relation="uap_encounter_article_rel",
        column1="article_id",
        column2="encounter_id",
        string="Encounters",
    )
    encounter_count = fields.Integer(
        string="# Encounters",
        compute="_compute_encounter_count",
    )

    def _compute_encounter_count(self):
        for rec in self:
            rec.encounter_count = len(rec.encounter_ids)

    def action_open_encounters(self):
        self.ensure_one()
        return {
            "type":      "ir.actions.act_window",
            "name":      "Encounters",
            "res_model": "uap.encounter",
            "view_mode": "list,form",
            "domain":    [("id", "in", self.encounter_ids.ids)],
            "context":   {"create": False},
        }

    def action_classify_uap(self):
        """Klassificera markerade (eller alla oklassificerade) artiklar via Claude.

        Samma prompt/kategorier som clio-tools/clio-uap/uap_classify.py (nattjobbet) —
        håll de två synkade manuellt om kategorierna ändras.
        """
        records = self if self.ids else self.search([("relevance_class", "=", "not_classified")])
        if not records:
            return
        from .uap_classify_odoo import classify_records
        classify_records(records)
