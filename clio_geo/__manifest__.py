{
    "name": "Clio Geo — Known Locations",
    "version": "19.0.1.1.0",
    "summary": "GPS-baserat register över kända platser för clio_vision och adresshantering",
    "author": "Arvas International AB",
    "license": "LGPL-3",
    "url": "https://github.com/FredrikArvas/clio-odoo-addons",
    "category": "Tools",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/clio_location_views.xml",
        "views/clio_location_overlap_views.xml",
        "views/menu.xml",
        "data/clio_location_data.xml",
    ],
    "installable": True,
    "application": False,
}
