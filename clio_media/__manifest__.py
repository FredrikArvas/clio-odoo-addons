{
    "name":        "Clio Media — Artikelarkiv",
    "version":     "19.0.1.1.0",
    "category":    "Extra Tools",
    "summary":     "Delad artikelbank för Clio-agenter (clio_job, clio_recruit, clio_vigil).",
    "author":      "Arvas International AB",
    "license":     "LGPL-3",
    "depends":     ["base"],
    "data": [
        "security/ir.model.access.csv",
        "data/clio_media_source_data.xml",
        "views/clio_media_article_views.xml",
        "views/clio_media_source_views.xml",
    ],
    "installable":  True,
    "auto_install": False,
    "application":  False,
}
