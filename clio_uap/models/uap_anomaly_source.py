from odoo import models, fields


class UapAnomalySource(models.Model):
    _name        = "uap.anomaly.source"
    _description = "UAP — Anomalikälla (spårbarhet)"
    _order       = "source_type, added_at desc"
    _rec_name    = "source_ref"

    anomaly_id = fields.Many2one(
        comodel_name="uap.anomaly",
        string="Anomali",
        required=True,
        ondelete="cascade",
        index=True,
    )
    source_type = fields.Selection(
        selection=[
            ("encounter", "Encounter (uap.encounter)"),
            ("podcast",   "Podd"),
            ("article",   "Artikel / Tidning"),
            ("webpage",   "Webbsida"),
            ("book",      "Bok"),
            ("document",  "Officiellt dokument"),
            ("other",     "Övrigt"),
        ],
        string="Källtyp",
        required=True,
    )
    encounter_id = fields.Many2one(
        comodel_name="uap.encounter",
        string="Encounter",
        ondelete="set null",
        help="Fylls i om källtyp är 'encounter'",
    )
    uap_source_id = fields.Many2one(
        comodel_name="uap.source",
        string="Källa (katalog)",
        ondelete="set null",
        help="Länk till källkatalogen om källan finns registrerad där",
    )
    source_ref = fields.Char(
        string="Källreferens",
        help="URL, ISBN, poddnamn + episod, dokumenttitel etc.",
    )
    timestamp_in_source = fields.Char(
        string="Position i källa",
        help="Tidsstämpel (00:42:15), radnummer (rad 847) eller sidnummer (s. 112)",
    )
    quote = fields.Text(
        string="Citat",
        help="Det specifika citat eller utdrag som stödjer kopplingen till anomalin",
    )
    added_at = fields.Datetime(
        string="Tillagd",
        default=fields.Datetime.now,
    )
