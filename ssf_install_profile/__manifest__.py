{
    'name': 'SSF — Installationsprofil',
    'version': '19.0.1.0.0',
    'summary': 'Meta-modul: installerar samtliga moduler for SSF-databasen (tavling, LOK, betalningar, CRM-behorigheter, interna Arvas-verktyg).',
    'author': 'Arvas International AB, Capgemini Sverige AB',
    'website': 'https://github.com/Svenska-Skidforbundet/ssf-odoo',
    'license': 'LGPL-3',
    'depends': [
        # SSF-specifika moduler
        'ssf_competition',           # Tavlingshantering och resultat
        'ssf_crm_access',            # CRM-behorigheter for SSF-roller
        'ssf_lok',                   # LOK-stod och bidragsadministration
        'ssf_payments',              # Startavgiftsbetalningar
        'ssf_person_admin',          # Chip-koder, SSFTiming-export, IOL-roller m.m.
        'odoo_partner_ssf',          # SSF-specifika partnerfalt
        # Clio-moduler (interna Arvas-verktyg)
        'clio_cockpit',
        'clio_discuss',
        'clio_graph',
        'clio_mail_admin',
        'clio_theme',
        # Svensk lokalisering
        'l10n_se_ssn',
        'l10n_se_partner',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
}
