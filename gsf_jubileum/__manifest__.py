{
    "name":        "GSF Jubileum",
    "version":     "19.0.1.0.0",
    "category":    "Extra Tools",
    "summary":     "Insamling av fastighetshistorier till Guldboda 80-årsjubileum.",
    "author":      "Fredrik Arvas / Arvas International AB",
    "license":     "LGPL-3",
    "depends":     ["base", "web", "portal", "website"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/gsf_jubileum_fastighet_views.xml",
        "views/gsf_jubileum_portal_templates.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "gsf_jubileum/static/src/css/interview.css",
            "gsf_jubileum/static/src/js/interview.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application":  True,
}
