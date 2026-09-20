# -*- coding: utf-8 -*-
{
    'name': 'AIAB — Installationsprofil',
    'version': '19.0.4.4.0',
    'summary': 'Meta-modul: installerar alla moduler for AIAB-databasen',
    'author': 'Arvas International AB',
    'license': 'LGPL-3',
    'url': 'https://github.com/FredrikArvas/clio-odoo-addons',
    'depends': [
        # â”€â”€ Clio-moduler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        'clio_cockpit',                               # Dashboard och startvy
        'clio_discuss',                               # Odoo Discuss-integration (Clio Bot)
        'clio_event_log',                             # Handelselogg
        'clio_geo',                                   # GPS-platsregister (clio.location)
        'clio_graph',                                 # Relationsgrafer mellan kontakter
        'clio_interview',                             # Intervjuer och anstallningsprocess
        'clio_job',                                   # Jobbartikelbevakning och profiler
        'clio_mail_admin',                            # E-postadministration och NCC-wizard
        'clio_mail_permissions',                      # Behorighetsstyrning for e-post
        'clio_ncc_project',                           # NCC-projektkort i Odoo
        'odoo_message_delete',                         # Radera mail.message/mail.mail (grupp: Radera meddelanden)
        'clio_recruit',                               # Passiv kandidatsourcing (clio-recruiter)
        'clio_theme',                                 # AIAB-fargkodning av navbar
        'clio_vigil',                                 # Mediebevakning
        # â”€â”€ Lokalisering â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        'l10n_se_partner',                            # Svenska adressfaltsordning
        'l10n_se_ssn',                                # Personnummer pa kontakter
        # â”€â”€ Odoo standard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        'partner_autocomplete',                       # Foretassokning via VAT/org.nr
        # â”€â”€ OCA / partner-contact â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        'partner_contact_birthdate',                  # Fodelsedag pa kontakter
        'partner_contact_personal_information_page',  # Personlig info-flik pa kontakter
        'partner_firstname',                          # Fornamn och efternamn som separata falt
        'partner_multi_relation',                     # Typade relationer mellan kontakter
        # â”€â”€ Bokio-integration â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        'invoice_bokio',                              # Synkar fakturor fran Bokio
        'invoice_bokio_portal',                       # Bokio fakturavy for kontakter
        'partner_bokio',                              # Kopplar Odoo-kontakter till Bokio
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
}
