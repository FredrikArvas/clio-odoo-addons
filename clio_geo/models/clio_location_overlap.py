from odoo import api, fields, models
from .clio_location import _haversine_m


class ClioLocationOverlapLine(models.TransientModel):
    _name = "clio.location.overlap.line"
    _description = "Overlapping location pair"
    _order = "distance_m"

    wizard_id = fields.Many2one("clio.location.overlap.wizard", ondelete="cascade")
    loc_a_id = fields.Many2one("clio.location", string="Plats A", readonly=True)
    loc_b_id = fields.Many2one("clio.location", string="Plats B", readonly=True)
    distance_m = fields.Integer("Avstånd (m)", readonly=True)
    radius_a = fields.Integer(related="loc_a_id.radius_m", string="Radie A")
    radius_b = fields.Integer(related="loc_b_id.radius_m", string="Radie B")

    def action_deactivate_b(self):
        self.loc_b_id.active = False
        return self.env["clio.location.overlap.wizard"].action_open()


class ClioLocationOverlapWizard(models.TransientModel):
    _name = "clio.location.overlap.wizard"
    _description = "Overlapping locations"

    line_ids = fields.One2many(
        "clio.location.overlap.line", "wizard_id", string="Överlappande par"
    )

    @api.model
    def action_open(self):
        locations = self.env["clio.location"].search([("lat", "!=", 0), ("lon", "!=", 0)])
        loc_list = list(locations)
        pairs = []
        for i, a in enumerate(loc_list):
            for b in loc_list[i + 1:]:
                dist = _haversine_m(a.lat, a.lon, b.lat, b.lon)
                if dist < min(a.radius_m, b.radius_m):
                    pairs.append((round(dist), a.id, b.id))
        pairs.sort()

        wizard = self.create({})
        line_model = self.env["clio.location.overlap.line"]
        for dist, a_id, b_id in pairs:
            line_model.create({"wizard_id": wizard.id, "loc_a_id": a_id, "loc_b_id": b_id, "distance_m": dist})

        return {
            "name": "Överlappande platser (%d par)" % len(pairs),
            "type": "ir.actions.act_window",
            "res_model": "clio.location.overlap.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "target": "new",
        }
