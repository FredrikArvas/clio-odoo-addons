from odoo import models, fields, api


class UapSeries(models.Model):
    _name        = "uap.series"
    _description = "UAP — Event Series"
    _order       = "date_start desc"
    _rec_name    = "name"

    name = fields.Char(string="Series Name", required=True)
    series_type = fields.Selection(
        selection=[
            ("wave",            "Wave"),
            ("swarm",           "Swarm"),
            ("recurring",       "Recurring"),
            ("single_extended", "Single Extended Event"),
            ("campaign",        "Campaign"),
        ],
        string="SerIestype",
        index=True,
    )
    date_start  = fields.Date(string="Start Date")
    date_end    = fields.Date(string="End Date")
    geo_lat     = fields.Float(string="Center Latitude",  digits=(10, 6))
    geo_lng     = fields.Float(string="Center Longitude", digits=(10, 6))
    bbox_km     = fields.Float(string="Radius (km)")
    country_ids = fields.Many2many("res.country", string="Countries")
    confidence  = fields.Float(string="Confidence", digits=(3, 2))
    status = fields.Selection(
        selection=[
            ("auto_pending",   "Auto — Pending Review"),
            ("auto_confirmed", "Auto — Confirmed"),
            ("confirmed",      "Manually Confirmed"),
            ("rejected",       "Rejected"),
        ],
        string="Status",
        default="auto_pending",
        index=True,
    )
    encounter_ids = fields.One2many("uap.encounter", "series_id", string="Encounters")
    encounter_count = fields.Integer(
        string="# Encounters",
        compute="_compute_encounter_count",
        store=False,
    )
    notes = fields.Text(string="Notes")

    @api.depends("encounter_ids")
    def _compute_encounter_count(self):
        for rec in self:
            rec.encounter_count = len(rec.encounter_ids)
