{
    "name": "SSF - Person Admin",
    "version": "19.0.1.1.0",
    "summary": "Chip-kod-hantering och SSFTiming-export for SSF.",
    "author": "Arvas International AB",
    "depends": ["ssf_competition", "ssf_crm_access"],
    "data": [
        "security/ir.model.access.csv",
        "views/ssf_person_chip_views.xml",
        "views/ssf_timing_export_views.xml",
        "views/ssf_timing_import_views.xml",
        "views/res_partner_views.xml",
        "views/menu.xml",
        "views/ssf_competition_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
