from odoo import fields, models


class ClioRagCollection(models.Model):
    _name        = "clio.rag.collection"
    _description = "Clio RAG — Tillgängligt korpus"
    _order       = "label"

    key = fields.Char(required=True, index=True, readonly=True)
    label = fields.Char(required=True, readonly=True)
    active = fields.Boolean(
        string = "Aktiv",
        default = False,
        help = "Styr om detta korpus visas i RAG-sökningens källval för den här databasen.",
    )

    _key_uniq = models.Constraint("UNIQUE (key)", "Detta korpus är redan registrerat.")

    def action_sync_collections(self):
        """Hämta hela listan över tillgängliga korpus från clio-service och
        skapa/uppdatera poster. Nya korpus läggs till som inaktiva; befintliga
        admin-val (active) rörs inte."""
        from .clio_rag import _call

        result = _call(self.env, "/rag/collections")
        collections = result.get("collections", [])
        existing = {c.key: c for c in self.search([])}
        created = 0
        for c in collections:
            key = c["key"]
            label = c["label"]
            if key in existing:
                if existing[key].label != label:
                    existing[key].label = label
            else:
                self.create({"key": key, "label": label, "active": False})
                created += 1

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "RAG-korpus synkade",
                "message": (
                    f"{created} nya korpus hittades — markera dem som aktiva för att visa dem."
                    if created else "Inga nya korpus — listan är redan uppdaterad."
                ),
                "sticky": False,
            },
        }
