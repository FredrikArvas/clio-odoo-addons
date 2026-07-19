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
