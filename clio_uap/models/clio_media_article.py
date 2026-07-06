from odoo import models


class ClioMediaArticleUap(models.Model):
    """Lägger bara till klassificeringsmetoden. relevance_class-fältet ägs av clio_media."""

    _inherit = "clio.media.article"

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
