from urllib.parse import unquote

from odoo import api, fields, models

AFU_FILES_URL = "https://files.afu.se/Downloads/"
AFU_FOLDER_DEPTH = 2   # "UFO-reports/Scandinavia" — tillräckligt för gruppering

ETH_SELECTION = [
    ("0", "0 — Förklarat/mänskligt"),
    ("1", "1 — Troligen mänskligt"),
    ("2", "2 — Okänt ursprung"),
    ("3", "3 — Stark icke-mänsklig indikation"),
    ("4", "4 — Officiellt korroborerat"),
    ("5", "5 — Officiellt bekräftat"),
]


class ClioMediaArticle(models.Model):
    """AFU-dokument = clio.media.article med URL under files.afu.se.

    Klassningsfälten skrivs av clio-afu/afu_classify_docs.py.
    mail.thread ger chatter (kommentarer) i formuläret.
    """
    _name = "clio.media.article"
    _inherit = ["clio.media.article", "mail.thread"]

    is_afu_document = fields.Boolean(
        string="AFU-dokument", compute="_compute_afu_path", store=True, index=True,
    )
    afu_folder = fields.Char(
        string="AFU-mapp", compute="_compute_afu_path", store=True, index=True,
    )

    is_afu_case_report = fields.Boolean(string="Fallrapport", index=True)
    afu_eth_origin = fields.Selection(ETH_SELECTION, string="ETH-ursprung")
    afu_intelligence_indicator = fields.Selection(
        [("0", "0"), ("1", "1"), ("2", "2"), ("3", "3")], string="Intelligensindikator",
    )
    afu_discourse_level = fields.Selection(
        [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")], string="Diskursnivå",
    )
    afu_craft_class = fields.Char(string="Farkostklass")
    afu_case_date = fields.Char(string="Händelsedatum")
    afu_case_year = fields.Integer(string="Händelseår", index=True)
    afu_location = fields.Char(string="Plats")
    afu_summary = fields.Text(string="Sammanfattning")
    afu_text_chars = fields.Integer(string="Texttecken")
    afu_classified_at = fields.Datetime(string="Klassad")

    @api.model_create_multi
    def create(self, vals_list):
        # Artiklar skapas i bulk av vigil/importer — ingen följare eller
        # "skapad"-logg per artikel; chattern är till för kommentarer.
        return super(
            ClioMediaArticle,
            self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True),
        ).create(vals_list)

    @api.depends("url")
    def _compute_afu_path(self):
        for rec in self:
            url = rec.url or ""
            rec.is_afu_document = url.startswith(AFU_FILES_URL)
            if not rec.is_afu_document:
                rec.afu_folder = False
                continue
            parts = unquote(url[len(AFU_FILES_URL):]).split("/")[:-1]
            rec.afu_folder = "/".join(parts[:AFU_FOLDER_DEPTH]) or False
