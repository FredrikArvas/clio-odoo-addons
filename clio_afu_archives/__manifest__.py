{
    'name': 'AFU Archives — Delad infrastruktur',
    'version': '19.0.2.0.0',
    'summary': 'Delad bas för AFU-källarkiv: attributtabell, källpublikationer och toppnivåmeny',
    'description': 'Bas-modul för alla clio_afu_*-moduler. Tillhandahåller afu.attribute och afu.archive.source.',
    'author': 'Arvas International AB',
    'website': 'https://github.com/FredrikArvas/clio-odoo-addons/tree/19.0/clio_afu_archives',
    'category': 'Research',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/afu_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
