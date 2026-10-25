from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestClioMediaWorkType(TransactionCase):

    def test_unique_work_type_code(self):
        self.env["clio.media.work.type"].create({"code": "test_unique", "name": "Test"})
        with self.assertRaises(Exception):
            self.env["clio.media.work.type"].create({"code": "test_unique", "name": "Dubblett"})


class TestClioMediaWork(TransactionCase):

    def setUp(self):
        super().setUp()
        self.book_type = self.env.ref("clio_media.work_type_book")

    def _make_work(self, name="Testverk", source_ref=None):
        vals = {"name": name, "work_type_id": self.book_type.id}
        if source_ref:
            vals["source_ref"] = source_ref
        return self.env["clio.media.work"].create(vals)

    def test_source_ref_unique_when_set(self):
        self._make_work("A", source_ref="notion-abc123")
        with self.assertRaises(Exception):
            self._make_work("B", source_ref="notion-abc123")

    def test_source_ref_multiple_nulls_allowed(self):
        # PostgreSQL UNIQUE tillåter flera NULL
        self._make_work("Verk 1")
        self._make_work("Verk 2")


class TestClioMediaWorkIdentifier(TransactionCase):

    def setUp(self):
        super().setUp()
        book_type = self.env.ref("clio_media.work_type_book")
        self.work = self.env["clio.media.work"].create(
            {"name": "Identifierartest", "work_type_id": book_type.id}
        )

    def _make_ident(self, scheme, value):
        return self.env["clio.media.work.identifier"].create(
            {"work_id": self.work.id, "scheme": scheme, "value": value}
        )

    def test_unique_scheme_value(self):
        self._make_ident("isbn", "9789100192655")
        with self.assertRaises(Exception):
            self._make_ident("isbn", "9789100192655")

    def test_isbn_normalization_strips_hyphens(self):
        ident = self._make_ident("isbn", "978-91-0-019265-5")
        self.assertEqual(ident.value, "9789100192655")

    def test_isbn_collision_after_normalization(self):
        self._make_ident("isbn", "9789100192655")
        with self.assertRaises(Exception):
            self._make_ident("isbn", "978-91-0-019265-5")

    def test_url_value_trimmed(self):
        ident = self._make_ident("url", "  https://example.com  ")
        self.assertEqual(ident.value, "https://example.com")
