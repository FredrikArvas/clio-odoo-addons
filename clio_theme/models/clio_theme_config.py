from odoo import api, fields, models


class ClioThemeConfig(models.Model):
    _name = 'clio.theme.config'
    _description = 'Clio Theme Configuration'
    _rec_name = 'id'

    navbar_bg     = fields.Char('Navbar bakgrund')
    navbar_border = fields.Char('Navbar accent/linje')
    navbar_text   = fields.Char('Navbar text')
    sidebar_bg    = fields.Char('Sidebar bakgrund')
    sidebar_text  = fields.Char('Sidebar text')
    primary_color = fields.Char('Primar accentfarg')

    @api.model
    def get_config(self):
        return self.sudo().search([], limit=1)