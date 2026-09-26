from odoo import models, fields, api


class LarryHatchCase(models.Model):
    _name = 'afu.larry_hatch.case'
    _description = 'Larry Hatch U* Case'
    _order = 'year_val, month_val, day_val'
    _rec_name = 'display_name'

    # Stable identifier
    content_hash = fields.Char(string='Content Hash', index=True, readonly=True)

    # Date/time
    year_val = fields.Integer(string='Year')
    month_val = fields.Integer(string='Month')   # 0 = unknown
    day_val = fields.Integer(string='Day')       # 0 = unknown
    hour_val = fields.Integer(string='Hour')
    minute_val = fields.Integer(string='Minute')
    duration = fields.Integer(string='Duration (min)')

    date_display = fields.Char(string='Date', compute='_compute_date_display', store=False)

    # Geography
    lat_deg = fields.Float(string='Latitude', digits=(10, 6))
    lon_deg = fields.Float(string='Longitude', digits=(10, 6))
    lat_dir = fields.Selection([('N', 'N'), ('S', 'S'), ('Q', 'Q?')], string='Lat Dir')
    lon_dir = fields.Selection([('E', 'E'), ('W', 'W'), ('Z', 'Z?')], string='Lon Dir')
    prec = fields.Char(string='Precision Code', size=4)

    # Location codes (3-char)
    continent = fields.Char(string='Continent', size=3, index=True)
    country = fields.Char(string='Country', size=3, index=True)
    state_code = fields.Char(string='State/Region', size=3, index=True)

    # Report metadata
    strangeness = fields.Integer(string='Strangeness (0–9)')
    credibility = fields.Integer(string='Credibility (0–9)')
    ref_no = fields.Integer(string='Ref #')
    page_no = fields.Integer(string='Page #')
    terrain = fields.Char(string='Terrain Code')

    # Summary
    summary = fields.Text(string='Summary')

    # Source tracking
    rnd_index = fields.Integer(string='RND Record Index', readonly=True)
    is_deleted = fields.Boolean(string='Deleted Record', default=False)

    display_name = fields.Char(compute='_compute_display_name', store=True)

    @api.depends('year_val', 'summary')
    def _compute_display_name(self):
        for rec in self:
            summ = (rec.summary or '')[:40]
            rec.display_name = f"{rec.year_val}: {summ}"

    @api.depends('year_val', 'month_val', 'day_val')
    def _compute_date_display(self):
        for rec in self:
            y = rec.year_val
            m = f"/{rec.month_val:02d}" if rec.month_val else ""
            d = f"/{rec.day_val:02d}" if rec.day_val else ""
            rec.date_display = f"{y}{m}{d}"
