{
    'name': 'Clio KEDS',
    'version': '19.0.1.0.0',
    'summary': 'KEDS - Karolinska Exhaustion Disorder Scale självskattning',
    'description': """
        Clio KEDS
        =========
        Självskattningstest för utmattningssyndrom baserat på
        KEDS (Karolinska Exhaustion Disorder Scale).
        Resultat kopplas till res.users och visas som trend över tid.
    """,
    'author': 'Arvas International AB',
    'website': 'https://arvas.international',
    'category': 'Extra Tools',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/clio_keds_security.xml',
        'security/ir.model.access.csv',
        'views/clio_keds_result_views.xml',
        'views/clio_keds_menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
