from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from psycopg2 import IntegrityError
from odoo.tools import mute_logger


class TestClioKedsResult(TransactionCase):
    """Enhetstester för clio.keds.result."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = cls.env['res.users'].create({
            'name': 'KEDS Test User A',
            'login': 'keds_test_a@test.local',
        })
        cls.user_b = cls.env['res.users'].create({
            'name': 'KEDS Test User B',
            'login': 'keds_test_b@test.local',
        })

    # ── Hjälpmetod ───────────────────────────────────────────────
    def _make(self, user=None, date='2024-01-15', **scores):
        vals = {
            'user_id': (user or self.user_a).id,
            'date': date,
            'q1': 0, 'q2': 0, 'q3': 0, 'q4': 0, 'q5': 0,
            'q6': 0, 'q7': 0, 'q8': 0, 'q9': 0,
        }
        vals.update(scores)
        return self.env['clio.keds.result'].create(vals)

    # ── Beräkning ────────────────────────────────────────────────
    def test_score_zero(self):
        """Alla nollor ger totalpoäng 0 och låg risk."""
        rec = self._make()
        self.assertEqual(rec.score, 0)
        self.assertEqual(rec.risk_level, 'low')

    def test_score_sum(self):
        """Totalpoäng är summan av alla 9 fält."""
        rec = self._make(q1=2, q2=2, q3=2, q4=2, q5=2, q6=2, q7=2, q8=2, q9=2)
        self.assertEqual(rec.score, 18)
        self.assertEqual(rec.risk_level, 'low')

    def test_score_high_risk_boundary(self):
        """Gräns vid 19 — precis ovanför ger hög risk."""
        # 2+2+2+2+2+2+2+2+3 = 19
        rec = self._make(q1=2, q2=2, q3=2, q4=2, q5=2, q6=2, q7=2, q8=2, q9=3)
        self.assertEqual(rec.score, 19)
        self.assertEqual(rec.risk_level, 'high')

    def test_score_below_boundary(self):
        """18 poäng ger fortfarande låg risk."""
        rec = self._make(q1=2, q2=2, q3=2, q4=2, q5=2, q6=2, q7=2, q8=2, q9=2)
        self.assertEqual(rec.score, 18)
        self.assertEqual(rec.risk_level, 'low')

    def test_score_max(self):
        """Maxpoäng 54 (9×6) ger hög risk."""
        rec = self._make(q1=6, q2=6, q3=6, q4=6, q5=6, q6=6, q7=6, q8=6, q9=6)
        self.assertEqual(rec.score, 54)
        self.assertEqual(rec.risk_level, 'high')

    # ── Beräknat namn ────────────────────────────────────────────
    def test_computed_name(self):
        """Namn byggs av användarnamn + datum."""
        rec = self._make(date='2024-03-10')
        self.assertIn('2024-03-10', rec.name)
        self.assertIn(self.user_a.name, rec.name)

    # ── Constraints: score-intervall ─────────────────────────────
    def test_score_below_zero_raises(self):
        """Negativt värde ska ge ValidationError."""
        with self.assertRaises(ValidationError):
            self._make(q1=-1)

    def test_score_above_six_raises(self):
        """Värde > 6 ska ge ValidationError."""
        with self.assertRaises(ValidationError):
            self._make(q5=7)

    def test_score_exact_six_ok(self):
        """Exakt 6 är tillåtet."""
        rec = self._make(q9=6)
        self.assertEqual(rec.q9, 6)

    def test_score_exact_zero_ok(self):
        """Exakt 0 är tillåtet."""
        rec = self._make(q1=0)
        self.assertEqual(rec.q1, 0)

    # ── Constraint: unik user+datum ──────────────────────────────
    @mute_logger('odoo.sql_db')
    def test_unique_user_date(self):
        """Duplicate user+datum ska blockeras av DB-constraint."""
        self._make(date='2024-06-01')
        with self.assertRaises(Exception):
            self._make(date='2024-06-01')

    def test_different_user_same_date_ok(self):
        """Samma datum för två olika användare är tillåtet."""
        r1 = self._make(user=self.user_a, date='2024-06-15')
        r2 = self._make(user=self.user_b, date='2024-06-15')
        self.assertTrue(r1.id)
        self.assertTrue(r2.id)

    def test_same_user_different_date_ok(self):
        """Samma användare på två olika datum är tillåtet."""
        r1 = self._make(date='2024-07-01')
        r2 = self._make(date='2024-07-02')
        self.assertTrue(r1.id)
        self.assertTrue(r2.id)

    # ── Recompute vid ändring ─────────────────────────────────────
    def test_score_recompute_on_write(self):
        """Ändring av ett delfält uppdaterar totalpoäng och risk."""
        rec = self._make()
        self.assertEqual(rec.score, 0)
        # q1-q8 = 2*8 = 16, q9 = 2 → total = 18, låg risk
        rec.write({'q1': 2, 'q2': 2, 'q3': 2, 'q4': 2, 'q5': 2,
                   'q6': 2, 'q7': 2, 'q8': 2, 'q9': 2})
        self.assertEqual(rec.score, 18)
        self.assertEqual(rec.risk_level, 'low')
        # Höj q9 med 1 → 18+1 = 19, ökad risk
        rec.write({'q9': 3})
        self.assertEqual(rec.score, 19)
        self.assertEqual(rec.risk_level, 'high')
