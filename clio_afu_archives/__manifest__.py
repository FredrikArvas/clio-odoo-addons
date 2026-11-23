{
    'name': 'AFU Archives — Delad infrastruktur',
    'version': '19.0.3.2.0',
    'summary': 'AFU-appen: toppnivåmeny, attribut/källor och AFU-dokument (klassade clio.media.article)',
    'description': 'Bas-modul för alla clio_afu_*-moduler. Tillhandahåller afu.attribute och afu.archive.source.',
    'author': 'Arvas International AB',
    'website': 'https://github.com/FredrikArvas/clio-odoo-addons/tree/19.0/clio_afu_archives',
    'category': 'Research',
    'depends': ['base', 'mail', 'clio_media'],
    'data': [
        'security/ir.model.access.csv',
        'views/afu_menus.xml',
        'views/afu_document_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
