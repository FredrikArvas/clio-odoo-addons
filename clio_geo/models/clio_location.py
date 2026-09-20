import math
from odoo import api, fields, models


def _haversine_m(lat1, lon1, lat2, lon2):
    """Return distance in metres between two GPS coordinates."""
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class ClioLocation(models.Model):
    _name = "clio.location"
    _description = "Known GPS Location"
    _order = "name"

    name = fields.Char(required=True)
    display_name_geo = fields.Char(
        required=True,
        help="Human-readable location string returned to clio_vision, e.g. 'Muskö, Sweden'",
    )
    lat = fields.Float(digits=(10, 7))
    lon = fields.Float(digits=(10, 7))
    radius_m = fields.Integer(
        default=200,
        string="Radius (m)",
        help="Match radius in metres. A GPS hit within this distance returns this location.",
    )
    category = fields.Selection(
        [
            ("home", "Home"),
            ("work", "Work"),
            ("vacation", "Vacation"),
            ("other", "Other"),
        ],
        default="other",
    )
    street = fields.Char()
    street_number = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    country_id = fields.Many2one("res.country")
    state_id = fields.Many2one("res.country.state")
    notes = fields.Text()
    active = fields.Boolean(default=True)

    map_url = fields.Char(
        compute="_compute_map_url",
        string="OSM Link",
    )
    map_iframe = fields.Html(
        compute="_compute_map_iframe",
        sanitize=False,
        string="Map",
    )

    @api.depends("lat", "lon")
    def _compute_map_url(self):
        for rec in self:
            if rec.lat and rec.lon:
                rec.map_url = (
                    f"https://www.openstreetmap.org/"
                    f"?mlat={rec.lat}&mlon={rec.lon}#map=15/{rec.lat}/{rec.lon}"
                )
            else:
                rec.map_url = False

    @api.depends("lat", "lon")
    def _compute_map_iframe(self):
        for rec in self:
            if rec.lat and rec.lon:
                margin = 0.008
                bbox = (
                    f"{rec.lon - margin},{rec.lat - margin},"
                    f"{rec.lon + margin},{rec.lat + margin}"
                )
                src = (
                    f"https://www.openstreetmap.org/export/embed.html"
                    f"?bbox={bbox}&layer=mapnik&marker={rec.lat},{rec.lon}"
                )
                rec.map_iframe = (
                    f'<iframe src="{src}" '
                    f'style="width:100%;height:300px;border:0;border-radius:4px"/>'
                )
            else:
                rec.map_iframe = ""

    @api.model
    def find_nearest(self, lat, lon):
        """Return display_name_geo for the nearest active location within its radius, or False."""
        locations = self.search([])
        best = None
        best_dist = float("inf")
        for loc in locations:
            if not loc.lat and not loc.lon:
                continue
            dist = _haversine_m(lat, lon, loc.lat, loc.lon)
            if dist <= loc.radius_m and dist < best_dist:
                best = loc
                best_dist = dist
        return best.display_name_geo if best else False
