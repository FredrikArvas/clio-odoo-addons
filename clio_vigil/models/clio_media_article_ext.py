from odoo import api, fields, models


class ClioMediaArticleVigilExt(models.Model):
    _inherit = "clio.media.article"

    vigil_item_id = fields.Many2one(
        comodel_name = "clio.vigil.item",
        string       = "Vigil-objekt",
        ondelete     = "set null",
        index        = True,
        help         = "Länk till det underliggande pipeline-objektet i clio.vigil.item.",
    )

    vigil_state = fields.Selection(
        related  = "vigil_item_id.state",
        string   = "Pipeline-status",
        store    = True,
        index    = True,
        readonly = True,
    )

    vigil_notified_at = fields.Datetime(
        related  = "vigil_item_id.notified_at",
        string   = "Skickad i digest",
        store    = True,
        index    = True,
        readonly = True,
    )

    vigil_notified_date = fields.Char(
        string  = "Skickad (datum)",
        compute = "_compute_vigil_notified_date",
        store   = True,
        index   = True,
    )

    @api.depends("vigil_notified_at")
    def _compute_vigil_notified_date(self):
        for rec in self:
            if rec.vigil_notified_at:
                rec.vigil_notified_date = rec.vigil_notified_at.strftime("%Y-%m-%d")
            else:
                rec.vigil_notified_date = False

    @api.depends("vigil_item_id")
    def _compute_audio_downloaded(self):
        for rec in self:
            item = rec.vigil_item_id
            rec.audio_downloaded = bool(item and item.archive_path)

    audio_downloaded = fields.Boolean(
        string  = "Nedladdad",
        compute = "_compute_audio_downloaded",
        store   = True,
    )

    def action_boost_vigil(self):
        """Delegerar till det underliggande clio.vigil.item:s action_boost()."""
        self.ensure_one()
        if not self.vigil_item_id:
            return
        return self.vigil_item_id.action_boost()
