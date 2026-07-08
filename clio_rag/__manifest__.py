{
    "name":        "Clio RAG — Kunskapsbas",
    "version":     "19.0.1.0.0",
    "category":    "Extra Tools",
    "summary":     "Fristående RAG-sökning mot Qdrant-kunskapsbaser, med per-databas urval av korpus.",
    "author":      "Fredrik Arvas / Arvas International AB",
    "license":     "LGPL-3",
    "depends":     ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/clio_rag_views.xml",
        "views/clio_rag_collection_views.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "clio_rag/static/src/js/rag_enter.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application":  True,
}
