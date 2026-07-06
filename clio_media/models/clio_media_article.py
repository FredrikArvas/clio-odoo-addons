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
    title       = fields.Char(string="Rubrik")
    source      = fields.Char(string="Källa")
    media_type  = fields.Selection(
        selection = [("article", "Artikel")],
        string    = "Typ",
        default   = "article",
    )
    published    = fields.Datetime(string="Publicerad")
    first_seen   = fields.Datetime(string="Först sedd")
    body_snippet = fields.Text(string="Utdrag")
    match_score  = fields.Integer(string="Score", default=-1)
    is_matched   = fields.Boolean(string="Matchad")

    # ── Medieanalys-fält (clio-research media_research-spår) ──────────────
    country = fields.Char(
        string = "Land",
        index  = True,
        help   = "ISO 3166-1 alpha-2 (SE, US, FR, BR).",
    )
    language = fields.Char(
        string = "Språk",
        help   = "ISO 639-1 (sv, en, fr, pt).",
    )
    author = fields.Char(
        string = "Journalist/Författare",
        index  = True,
        help   = "Byline — lämnas tomt om ej tillgängligt via datakällan.",
    )
    tone = fields.Selection(
        selection = [
            ("neutral_faktabaserad", "Neutral / Faktabaserad"),
            ("skeptisk",             "Skeptisk"),
            ("sensationalistisk",    "Sensationalistisk"),
            ("oklar",                "Oklar"),
        ],
        string = "Ton",
        index  = True,
    )
    article_type = fields.Selection(
        selection = [
            ("reaktiv",  "Reaktiv"),
            ("proaktiv", "Proaktiv"),
            ("oklar",    "Oklar"),
        ],
        string = "Artikeltyp",
    )
    thematic_frame = fields.Selection(
        selection = [
            ("nationell_sakerhet",    "Nationell säkerhet"),
            ("vetenskap_astronomi",   "Vetenskap / Astronomi"),
            ("konspirationsteori",    "Konspirationsteori"),
            ("folklig_kultur",        "Folklig kultur"),
            ("politisk_transparens",  "Politisk transparens"),
            ("okategoriserad",        "Okategoriserad"),
        ],
        string = "Tematisk inramning",
        index  = True,
    )
    cited_actors = fields.Char(
        string = "Citerade aktörer",
        help   = "Kommaseparerade kategorier: militär, myndighet, forskare, vittne, politiker, skeptiker, ufolog_civilsamhälle.",
    )
    temporal_marker_match = fields.Char(
        string = "Tidsmarkör (YYYY-MM-DD)",
        help   = "Datum för den tidsmarkör som utlöste artikeln (±30 dagar), om identifierad.",
    )
    data_source = fields.Selection(
        selection = [
            ("gdelt",           "GDELT"),
            ("vigil_ufo",       "vigil_ufo"),
            ("google_news_rss", "Google News RSS"),
        ],
        string = "Datakälla",
        help   = "Vilken connector som hämtade artikeln.",
    )
    run_id      = fields.Char(string="clio-research körning", index=True)
    protocol_id = fields.Char(string="Protokoll-ID", index=True)
    is_false_positive = fields.Boolean(
        string="Ej UAP-relevant",
        default=False,
        index=True,
        help="Markera om artikeln inte handlar om UAP/UFO i relevant bemärkelse (t.ex. teaterföreställning, metafor).",
    )

    body = fields.Text(
        string="Artikeltext",
        help="Fullständig artikeltext. Upphovsrätt tillhör respektive utgivare.",
    )
    fetch_status = fields.Selection(
        selection=[
            ("not_fetched", "Ej hämtad"),
            ("success",     "Hämtad"),
            ("partial",     "Delvis (betalvägg)"),
            ("paywalled",   "Betalvägg"),
            ("error",       "Fel"),
        ],
        string="Hämtstatus",
        default="not_fetched",
        index=True,
    )
    is_personal_use = fields.Boolean(
        string="Privat bruk",
        default=False,
        help="Markera att innehållet lagras för privat bruk. Upphovsrätt tillhör respektive utgivare — får ej vidaredistribueras.",
    )

    relevance_class = fields.Selection(
        selection=[
            ("not_classified", "Oklassificerad"),
            ("confirmed",      "Bekräftad UAP"),
            ("likely",         "Trolig UAP"),
            ("uncertain",      "Osäker"),
            ("off_topic",      "Ej UAP (film/spel/metafor)"),
        ],
        string="Klassificering",
        default="not_classified",
        index=True,
    )
    journalist_ids = fields.Many2many(
        comodel_name = 'res.partner',
        relation     = 'clio_media_article_journalist_rel',
        column1      = 'article_id',
        column2      = 'partner_id',
        string       = 'Journalister',
        help         = 'Länkade journalister som res.partner — inkl. e-post.',
    )
