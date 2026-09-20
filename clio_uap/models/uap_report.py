from odoo import models, fields


class UapReport(models.Model):
    _name        = "uap.report"
    _description = "UAP — Raw Import Report"
    _order       = "report_date desc"
    _rec_name    = "raw_title"

    database_id     = fields.Many2one("uap.database", string="Source Database", index=True, ondelete="restrict")
    import_batch    = fields.Char(string="Import Batch", index=True)
    external_id     = fields.Char(string="External ID", index=True)
    raw_title       = fields.Char(string="Title")
    raw_description = fields.Text(string="Description")
    report_date     = fields.Datetime(string="Observation Date")
    posted_date     = fields.Datetime(string="Posted Date")
    country_id      = fields.Many2one("res.country", string="Country", index=True)
    location_text   = fields.Char(string="Location")
    geo_lat         = fields.Float(string="Latitude",  digits=(10, 6))
    geo_lng         = fields.Float(string="Longitude", digits=(10, 6))
    reporter_type = fields.Selection(
        selection=[
            ("civilian", "Civilian"), ("military", "Military"), ("pilot", "Pilot / Aviation"),
            ("official", "Official"), ("unknown", "Unknown"),
        ],
        string="Reporter Type",
        default="unknown",
    )
    shape         = fields.Char(string="Object Shape")
    duration_text = fields.Char(string="Duration")
    status = fields.Selection(
        selection=[
            ("unlinked", "Unlinked"), ("linked", "Linked to Encounter"),
            ("duplicate", "Duplicate"), ("rejected", "Rejected"),
        ],
        string="Status",
        default="unlinked",
        index=True,
    )
    encounter_id  = fields.Many2one("uap.encounter", string="Encounter", index=True, ondelete="set null")
    canonical_id  = fields.Many2one("uap.report", string="Canonical Report", ondelete="set null")
    duplicate_ids = fields.One2many("uap.report", "canonical_id", string="Duplicates")

    # --- Skywatcher-klassificering (heuristisk, baserad på shape-fältet) ---
    skywatcher_class = fields.Selection(
        selection=[
            ("I",    "I — Tetra"),
            ("II",   "II — Tic Tac"),
            ("III",  "III — Blob"),
            ("IV",   "IV — Beam"),
            ("V",    "V — Manta Ray"),
            ("VI",   "VI — Bright Star"),
            ("VII",  "VII — Jellyfish"),
            ("VIII", "VIII — Hornet"),
            ("IX",   "IX — Egg"),
            ("X",    "X — Teardrop"),
        ],
        string="Skywatcher Class",
        index=True,
        help="Heuristisk Skywatcher-klass baserad på shape-fältet (auto_low konfidensgrad); X=Teardrop (eget tillägg)",
    )
    skywatcher_confidence = fields.Selection(
        selection=[
            ("auto_high", "Auto — hög"),
            ("auto_low",  "Auto — låg"),
            ("manual",    "Manuell"),
        ],
        string="SW Confidence",
        help="Källan till Skywatcher-klassificeringen på rårapportnivå",
    )
