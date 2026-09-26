from odoo import models, fields
from .afu_attribute import ARCHIVE_SELECTION


class AfuArchiveSource(models.Model):
    _name = 'afu.archive.source'
    _description = 'AFU Archive Source Publication'
    _order = 'archive, code'
    _rec_name = 'title'

    code = fields.Char(string='Code', size=20, index=True, required=True)
    title = fields.Char(string='Title', size=200, required=True)
    authors = fields.Char(string='Authors', size=200)
    year = fields.Integer(string='Year')
    journal = fields.Char(string='Journal/Publisher', size=200)
    url = fields.Char(string='URL', size=500)
    archive = fields.Selection(ARCHIVE_SELECTION, string='Archive', required=True, index=True)

    _sql_constraints = [
        ('code_archive_unique', 'UNIQUE(code, archive)', 'Source code must be unique per archive'),
    ]
