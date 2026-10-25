{
    "name":     "Clio — E-postbehörigheter",
    "version":  "19.0.1.0.0",
    "website": "https://github.com/FredrikArvas/clio-odoo-addons/tree/19.0/clio_mail_permissions",
    "summary":  "Behörighetshantering för clio-agent-mail med tvåvägssynk",
    "depends":  ["base", "clio_mail_admin"],
    "application": False,
    "data": [
        "security/ir.model.access.csv",
        "views/clio_mail_permission_views.xml",
    ],
}
