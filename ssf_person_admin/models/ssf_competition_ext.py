from odoo import models

class SsfCompetitionPersonAdmin(models.Model):
    _inherit = "ssf.competition"

    def action_export_ssftiming(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Exportera SSFTiming",
            "res_model": "ssf.timing.export",
            "view_mode": "form",
            "target": "new",
            "context": {"default_competition_id": self.id},
        }

    def action_import_ssftiming_results(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Importera SSFTiming-resultat",
            "res_model": "ssf.timing.result.import",
            "view_mode": "form",
            "target": "new",
            "context": {"default_competition_id": self.id},
        }
