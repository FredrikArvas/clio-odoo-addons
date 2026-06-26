from odoo import fields, models


class ClioMediaSource(models.Model):
    _name        = "clio.media.source"
    _description = "Clio Media — Nyhetskälla"
    _order       = "sequence, name"
    _rec_name    = "name"

    name = fields.Char(
        string   = "Namn",
        required = True,
        help     = "Visningsnamn, t.ex. 'Di — Näringsliv'.",
    )
    url = fields.Char(
        string   = "URL",
        required = True,
        help     = "RSS-flödets URL.",
    )
    source_type = fields.Selection(
        selection = [("rss", "RSS")],
        string    = "Typ",
        default   = "rss",
        required  = True,
    )
    enabled = fields.Boolean(
        string  = "Aktiv",
        default = True,
    )
    description = fields.Char(
        string = "Beskrivning",
        help   = "Kort anteckning om källans innehåll.",
    )
    sequence = fields.Integer(default=10)
