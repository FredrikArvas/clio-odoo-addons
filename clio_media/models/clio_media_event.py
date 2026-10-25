from odoo import fields, models


class ClioMediaEvent(models.Model):
    _name = "clio.media.event"
    _description = "Clio Media — Evenemang"
    _order = "date_start desc"
    _rec_name = "name"

    name = fields.Char(string="Evenemang", required=True)
    event_type = fields.Selection(
        selection=[
            ("conference",  "Konferens"),
            ("symposium",   "Symposium"),
            ("summit",      "Summit"),
            ("workshop",    "Workshop"),
            ("webinar",     "Webinar"),
        ],
        string="Typ",
        default="conference",
    )
    organizer = fields.Char(string="Arrangör")
    url = fields.Char(string="URL")
    date_start = fields.Date(string="Startdatum")
    date_end = fields.Date(string="Slutdatum")
    location = fields.Char(string="Plats", help="Online, stad eller venue")
    description = fields.Text(string="Beskrivning")
    article_ids = fields.One2many(
        comodel_name="clio.media.article",
        inverse_name="event_id",
        string="Presentationer",
    )
    presentation_count = fields.Integer(
        string="# Presentationer",
        compute="_compute_presentation_count",
        store=False,
    )

    attendee_ids = fields.Many2many(
        comodel_name = 'res.partner',
        relation     = 'clio_media_event_attendee_rel',
        column1      = 'event_id',
        column2      = 'partner_id',
        string       = 'Deltagare',
    )
    attendee_count = fields.Integer(
        string  = '# Deltagare',
        compute = '_compute_attendee_count',
        store   = False,
    )

    def _compute_attendee_count(self):
        for rec in self:
            rec.attendee_count = len(rec.attendee_ids)

    def _compute_presentation_count(self):
        for rec in self:
            rec.presentation_count = len(rec.article_ids)
