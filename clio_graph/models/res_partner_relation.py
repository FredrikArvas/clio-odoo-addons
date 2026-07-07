"""
res_partner_relation.py
Utökar res.partner.relation (från OCA partner_multi_relation) med Neo4j-synkflaggor
och en server action för att synka "delar adress med"-relationer.
"""

from collections import defaultdict

from odoo import models, fields, api


class ResPartnerRelation(models.Model):
    _inherit = "res.partner.relation"

    sync_to_neo4j = fields.Boolean(
        string="Sync to Neo4j",
        default=True,
        help="Markera om denna relation ska speglas till Neo4j-grafsdatabasen.",
    )
    neo4j_synced_at = fields.Datetime(
        string="Last Synced",
        readonly=True,
        help="Tidpunkt när relationen senast skrevs till Neo4j.",
    )

    @api.model
    def action_sync_address_relations(self):
        """Synka "delar adress med"-relationer utifrån (street, zip, city).

        Grupperar aktiva, icke-företags partners på normaliserad adress och
        skapar/tar bort symmetriska relationer så grupperna alltid speglar
        nuvarande adressdata. Idempotent - säker att köra om.
        """
        rel_type = self.env.ref("clio_graph.rel_type_delar_adress")
        partners = self.env["res.partner"].search([
            ("active", "=", True),
            ("is_company", "=", False),
            ("street", "!=", False),
        ])

        groups = defaultdict(list)
        for partner in partners:
            key = (
                (partner.street or "").strip().lower(),
                (partner.zip or "").strip(),
                (partner.city or "").strip().lower(),
            )
            if key[0]:
                groups[key].append(partner)

        wanted_pairs = set()
        for members in groups.values():
            if len(members) < 2:
                continue
            members = sorted(members, key=lambda p: p.id)
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    wanted_pairs.add((members[i].id, members[j].id))

        existing = self.search([("type_id", "=", rel_type.id)])
        existing_pairs = {(r.left_partner_id.id, r.right_partner_id.id) for r in existing}

        to_create = wanted_pairs - existing_pairs
        to_remove = existing.filtered(
            lambda r: (r.left_partner_id.id, r.right_partner_id.id) not in wanted_pairs
        )

        for left_id, right_id in to_create:
            self.create({
                "left_partner_id": left_id,
                "right_partner_id": right_id,
                "type_id": rel_type.id,
            })

        removed_count = len(to_remove)
        if to_remove:
            to_remove.unlink()

        message = self.env._(
            "Skapade %(created)s, tog bort %(removed)s. Totalt %(total)s par.",
            created=len(to_create),
            removed=removed_count,
            total=len(wanted_pairs),
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": self.env._("Adressrelationer synkade"),
                "message": message,
                "type": "success",
                "sticky": False,
            },
        }
