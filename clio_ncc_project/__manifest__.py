{
    'name': 'Clio Context Cards',
    'version': '19.0.1.1.0',
    'summary': 'Projektlista med NCC-status — hämtad från Notion via clio-service',
    'author': 'Arvas International AB',
    'category': 'Clio',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/clio_ncc_project_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'website': 'https://github.com/FredrikArvas/clio-odoo-addons/tree/19.0/clio_ncc_project',
}
