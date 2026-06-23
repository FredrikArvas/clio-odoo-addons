from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ClioThemeConfig(models.Model):
    _name = 'clio.theme.config'
    _description = 'Clio Theme Configuration'
    _rec_name = 'id'

    navbar_bg     = fields.Char('Navbar-bakgrund')
    navbar_border = fields.Char('Navbar-accent/linje')
    navbar_text   = fields.Char('Navbar-text')
    sidebar_bg    = fields.Char('Sidofält bakgrund')
    sidebar_text  = fields.Char('Sidofält text')
    primary_color = fields.Char('Primär accentfärg')

    @api.model_create_multi
    def create(self, vals_list):
        if self.sudo().search_count([]) + len(vals_list) > 1:
            raise UserError(_(
                'Bara ett temainställningsrecord får finnas per databas. '
                'Redigera det befintliga recordet istället.'
            ))
        return super().create(vals_list)

    @api.model
    def get_config(self):
        return self.sudo().search([], limit=1)