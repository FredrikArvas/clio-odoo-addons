from odoo import models, fields

ARCHIVE_SELECTION = [
    ('larry_hatch', 'Larry Hatch U*'),
    ('robert_moore', 'Robert Moore PrimeBase'),
    ('usocat', 'Marco Bianchini USOcat'),
    ('navcat', 'Jan Aldrich NavCAT'),
    ('generic', 'Generic'),
]


class AfuAttribute(models.Model):
    _name = 'afu.attribute'
    _description = 'AFU Archive Attribute'
    _order = 'archive, row, col'
    _rec_name = 'name'

    code = fields.Char(string='Code', size=8, index=True, required=True)
    name = fields.Char(string='Name', size=80, required=True)
    archive = fields.Selection(ARCHIVE_SELECTION, string='Archive', required=True, index=True)
    row = fields.Integer(string='Row')
    col = fields.Integer(string='Col')
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('code_archive_unique', 'UNIQUE(code, archive)', 'Attribute code must be unique per archive'),
    ]
