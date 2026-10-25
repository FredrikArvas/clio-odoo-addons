from odoo import fields, models


class ClioMediaWork(models.Model):
    _name = "clio.media.work"
    _description = "Clio Media — Verk"
    _inherit = ["image.mixin"]
    _order = "name"
    _rec_name = "name"

    name = fields.Char(string="Titel", required=True)
    work_type_id = fields.Many2one(
        "clio.media.work.type",
        string="Verkstyp",
        required=True,
        index=True,
        ondelete="restrict",
    )
    author = fields.Char(string="Upphovsperson")
    year = fields.Integer(string="År")
    description = fields.Html(string="Beskrivning", sanitize=True)
    genre_ids = fields.Many2many(
        "clio.media.genre",
        relation="clio_media_work_genre_rel",
        column1="work_id",
        column2="genre_id",
        string="Genrer",
    )
    source_ref = fields.Char(
        string="Extern referens",
        index=True,
        help="Extern nyckel för idempotent import (t.ex. Notion-id). Unik när satt.",
    )
    identifier_ids = fields.One2many(
        "clio.media.work.identifier",
        "work_id",
        string="Identifierare",
    )

    # PostgreSQL tillåter flera NULL i UNIQUE — flera verk utan source_ref är ok
    _unique_source_ref = models.Constraint(
        "UNIQUE(source_ref)",
        "Extern referens (source_ref) måste vara unik.",
    )
