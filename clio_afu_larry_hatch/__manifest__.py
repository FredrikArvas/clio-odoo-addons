{
    'name': 'AFU Archives — Larry Hatch U*',
    'version': '19.0.1.0.0',
    'summary': 'Larry Hatch *U* UFO-databas (18 122 poster) portad till Odoo',
    'description': 'Importerar och exponerar Larry Hatchs klassiska U* database (U.RND) som Odoo-poster.',
    'author': 'Arvas International AB',
    'website': 'https://github.com/FredrikArvas/clio-odoo-addons/tree/19.0/clio_afu_larry_hatch',
    'category': 'Research',
    'depends': ['clio_afu_archives'],
    'data': [
        'security/ir.model.access.csv',
        'views/larry_hatch_case_views.xml',
        'views/larry_hatch_menus.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
