import re
from odoo import api, fields, models


class ClioMediaWorkIdentifier(models.Model):
    _name = "clio.media.work.identifier"
    _description = "Clio Media — Extern identifierare"
    _order = "scheme, value"

    SCHEME_SELECTION = [
        ("isbn", "ISBN"),
        ("spotify", "Spotify"),
        ("tmdb", "TMDB"),
        ("musicbrainz", "MusicBrainz"),
        ("notion", "Notion"),
        ("url", "URL"),
    ]

    work_id = fields.Many2one(
        "clio.media.work",
        string="Verk",
        required=True,
        ondelete="cascade",
        index=True,
    )
    scheme = fields.Selection(
        SCHEME_SELECTION,
        string="Schema",
        required=True,
    )
    value = fields.Char(string="Värde", required=True, index=True)

    link_url = fields.Char(
        string="Länk",
        compute="_compute_link_url",
        help="Klickbar länk baserad på schema och värde.",
    )

    _unique_scheme_value = models.Constraint(
        "UNIQUE(scheme, value)",
        "Kombinationen schema + värde måste vara unik.",
    )

    @api.depends("scheme", "value")
    def _compute_link_url(self):
        for rec in self:
            if not rec.value:
                rec.link_url = False
                continue
            if rec.scheme == "spotify":
                rec.link_url = f"https://open.spotify.com/track/{rec.value}"
            elif rec.scheme == "tmdb":
                rec.link_url = f"https://www.themoviedb.org/movie/{rec.value}"
            elif rec.scheme == "musicbrainz":
                rec.link_url = f"https://musicbrainz.org/recording/{rec.value}"
            elif rec.scheme == "url":
                rec.link_url = rec.value
            else:
                rec.link_url = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._normalize_identifier(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._normalize_identifier(vals)
        return super().write(vals)

    @staticmethod
    def _normalize_identifier(vals):
        scheme = vals.get("scheme")
        value = vals.get("value")
        if not value:
            return
        if scheme == "isbn":
            vals["value"] = re.sub(r"[\-\s]", "", value)
        elif scheme == "url":
            vals["value"] = value.strip()
