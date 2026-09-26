{
    'name': 'AFU Archives — Larry Hatch U* Database',
    'version': '19.0.1.0.0',
    'summary': 'Larry Hatch *U* UFO-databas (18 122 poster) portad till Odoo',
    'description': 'Importerar och exponerar Larry Hatchs klassiska U* database (U.RND) som Odoo-poster.',
    'author': 'Arvas International AB',
    'category': 'Research',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/larry_hatch_case_views.xml',
        'views/larry_hatch_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
