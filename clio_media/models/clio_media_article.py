from odoo import fields, models


class ClioMediaArticle(models.Model):
    _name        = "clio.media.article"
    _description = "Clio Media — Artikel"
    _order       = "first_seen desc"
    _rec_name    = "title"

    article_id  = fields.Char(
        string = "Artikel-ID",
        index  = True,
        help   = "Extern nyckel från agenten (t.ex. hash av URL).",
    )
    url = fields.Char(
        string = "URL",
        index  = True,
    )
    title = fields.Char(string="Rubrik")
    source = fields.Char(string="Källa")
    media_type = fields.Selection(
        selection = [("article", "Artikel")],
        string    = "Typ",
        default   = "article",
    )
    published   = fields.Datetime(string="Publicerad")
    first_seen  = fields.Datetime(string="Först sedd")
    body_snippet = fields.Text(string="Utdrag")
    match_score = fields.Integer(string="Score", default=-1)
    is_matched  = fields.Boolean(string="Matchad")
