from odoo import models, fields, api


class UapAnomaly(models.Model):
    _name        = "uap.anomaly"
    _description = "UAP — Anomali / Fenomen"
    _order       = "anomaly_type, name"
    _rec_name    = "name"

    name = fields.Char(string="Namn", required=True)
    anomaly_type = fields.Selection(
        selection=[
            ("biological",   "Biologisk / Botanisk"),
            ("atmospheric",  "Atmosfärisk / Sensorisk"),
            ("contact",      "Kontakt / Vittne"),
            ("geographic",   "Geografisk / Arkitektonisk"),
            ("military",     "Militär / Programmatisk"),
            ("cosmological", "Kosmologisk / Geometrisk"),
            ("transmorf",    "Transmorf — Varelse"),
            ("vehicle",      "Transmorf — Farkost"),
            ("other",        "Övrigt"),
        ],
        string="Typ",
        required=True,
        index=True,
    )
    description = fields.Text(string="Beskrivning")

    # --- Geografi ---
    location = fields.Text(string="Plats")
    geo_lat   = fields.Float(string="Latitud",  digits=(10, 6))
    geo_lng   = fields.Float(string="Longitud", digits=(10, 6))
    radius_km = fields.Float(string="Radie (km)")

    # --- Tidsperiod ---
    date_first = fields.Date(string="Första händelse")
    date_last  = fields.Date(string="Senaste händelse")

    # --- Bedömning ---
    confidence = fields.Selection(
        selection=[
            ("0", "0 — Obekräftat / Rykten"),
            ("1", "1 — Enskild källa"),
            ("2", "2 — Flera oberoende källor"),
            ("3", "3 — Fysisk evidens"),
            ("4", "4 — Officiellt erkänt"),
            ("5", "5 — Bekräftat / Declassified"),
        ],
        string="Konfidensgrad",
        index=True,
    )
    eth_relevance = fields.Selection(
        selection=[
            ("0", "0 — Ingen ETH-relevans"),
            ("1", "1 — Svag koppling"),
            ("2", "2 — Möjlig koppling"),
            ("3", "3 — Trolig koppling"),
            ("4", "4 — Stark koppling"),
            ("5", "5 — Bekräftat ETH-samband"),
        ],
        string="ETH-relevans",
        help="Koppling till icke-mänsklig / utomjordisk hypotes (0=ingen, 5=bekräftat)",
    )
    status = fields.Selection(
        selection=[
            ("draft",    "Utkast"),
            ("active",   "Aktiv"),
            ("archived", "Arkiverad"),
        ],
        string="Status",
        default="draft",
        index=True,
    )
    notes = fields.Text(string="Anteckningar")

    # --- Relationer ---
    source_ids = fields.One2many(
        comodel_name="uap.anomaly.source",
        inverse_name="anomaly_id",
        string="Källor",
    )
    encounter_ids = fields.Many2many(
        comodel_name="uap.encounter",
        relation="uap_anomaly_encounter_rel",
        column1="anomaly_id",
        column2="encounter_id",
        string="Encounters",
    )

    # --- Computed counts ---
    source_count = fields.Integer(
        string="# Källor",
        compute="_compute_counts",
        store=False,
    )
    encounter_count = fields.Integer(
        string="# Encounters",
        compute="_compute_counts",
        store=False,
    )

    @api.depends("source_ids", "encounter_ids")
    def _compute_counts(self):
        for rec in self:
            rec.source_count    = len(rec.source_ids)
            rec.encounter_count = len(rec.encounter_ids)
