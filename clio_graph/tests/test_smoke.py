from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSmokeClioGraph(TransactionCase):
    """Smoke test — clio_graph: verifierar att fälten är tillagda."""

    def test_relation_fields_added(self):
        """res.partner.relation ska ha clio_graph-fälten."""
        self.assertIn("res.partner.relation", self.env)
        fields = self.env["res.partner.relation"]._fields
        self.assertIn("sync_to_neo4j", fields)
        self.assertIn("neo4j_synced_at", fields)

    def test_relation_searchable(self):
        """res.partner.relation ska gå att söka utan fel."""
        relations = self.env["res.partner.relation"].search([], limit=5)
        # Ingen exception == OK

    def test_sync_field_default(self):
        """sync_to_neo4j ska ha False som default."""
        p1 = self.env["res.partner"].create({"name": "Graph-partner-A"})
        p2 = self.env["res.partner"].create({"name": "Graph-partner-B"})
        rel_type = self.env["res.partner.relation.type"].search([], limit=1)
        if rel_type:
            rel = self.env["res.partner.relation"].create({
                "left_partner_id": p1.id,
                "right_partner_id": p2.id,
                "type_id": rel_type.id,
            })
            self.assertFalse(rel.sync_to_neo4j)

    def test_action_sync_address_relations(self):
        """action_sync_address_relations ska koppla ihop partners med samma adress."""
        p1 = self.env["res.partner"].create({
            "name": "Adress-partner-A",
            "street": "Testvägen 1",
            "zip": "123 45",
            "city": "Testby",
        })
        p2 = self.env["res.partner"].create({
            "name": "Adress-partner-B",
            "street": "Testvägen 1",
            "zip": "123 45",
            "city": "Testby",
        })
        result = self.env["res.partner.relation"].action_sync_address_relations()
        self.assertEqual(result.get("type"), "ir.actions.client")

        rel_type = self.env.ref("clio_graph.rel_type_delar_adress")
        relation = self.env["res.partner.relation"].search([
            ("type_id", "=", rel_type.id),
            ("left_partner_id", "=", p1.id),
            ("right_partner_id", "=", p2.id),
        ])
        self.assertTrue(relation)
