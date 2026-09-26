{
    'name': 'AFU Archives — Delad infrastruktur',
    'version': '19.0.2.0.0',
    'summary': 'Delad bas för AFU-källarkiv: attributtabell, källpublikationer och toppnivåmeny',
    'description': 'Bas-modul för alla clio_afu_*-moduler. Tillhandahåller afu.attribute och afu.archive.source.',
    'author': 'Arvas International AB',
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
