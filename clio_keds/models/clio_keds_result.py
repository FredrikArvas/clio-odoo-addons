from odoo import api, fields, models
from odoo.exceptions import ValidationError


SCORE_HELP = "0 = inget besvär · 2 = ibland · 4 = ofta · 6 = maximalt besvär"


class ClioKedsResult(models.Model):
    _name = 'clio.keds.result'
    _description = 'KEDS Självskattning'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ── Identitet ────────────────────────────────────────────────
    name = fields.Char(
        string='Referens',
        compute='_compute_name',
        store=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Användare',
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )
    date = fields.Date(
        string='Datum',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )

    # ── De 9 KEDS-frågorna (0–6) ─────────────────────────────────
    q1 = fields.Integer(
        string='1. Koncentrationsförmåga',
        default=0,
        help=SCORE_HELP,
    )
    q2 = fields.Integer(
        string='2. Minne',
        default=0,
        help=SCORE_HELP,
    )
    q3 = fields.Integer(
        string='3. Kroppslig uttröttbarhet',
        default=0,
        help=SCORE_HELP,
    )
    q4 = fields.Integer(
        string='4. Uthållighet',
        default=0,
        help=SCORE_HELP,
    )
    q5 = fields.Integer(
        string='5. Återhämtningsförmåga',
        default=0,
        help=SCORE_HELP,
    )
    q6 = fields.Integer(
        string='6. Sömn',
        default=0,
        help=SCORE_HELP,
    )
    q7 = fields.Integer(
        string='7. Överkänslighet för sinnesintryck',
        default=0,
        help=SCORE_HELP,
    )
    q8 = fields.Integer(
        string='8. Upplevelse av krav',
        default=0,
        help=SCORE_HELP,
    )
    q9 = fields.Integer(
        string='9. Irritation och ilska',
        default=0,
        help=SCORE_HELP,
    )

    # ── Beräknade fält ───────────────────────────────────────────
    score = fields.Integer(
        string='Totalpoäng',
        compute='_compute_score',
        store=True,
        tracking=True,
    )
    risk_level = fields.Selection(
        selection=[
            ('low', 'Låg risk (< 19)'),
            ('high', 'Ökad risk (≥ 19)'),
        ],
        string='Risknivå',
        compute='_compute_score',
        store=True,
        tracking=True,
    )

    notes = fields.Text(string='Anteckningar')

    # ── Compute ──────────────────────────────────────────────────
    @api.depends('user_id', 'date')
    def _compute_name(self):
        for rec in self:
            user = rec.user_id.name or ''
            date = rec.date or ''
            rec.name = f"KEDS {user} {date}"

    @api.depends('q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9')
    def _compute_score(self):
        for rec in self:
            total = rec.q1 + rec.q2 + rec.q3 + rec.q4 + rec.q5 \
                  + rec.q6 + rec.q7 + rec.q8 + rec.q9
            rec.score = total
            rec.risk_level = 'high' if total >= 19 else 'low'

    # ── Constraints ──────────────────────────────────────────────
    _unique_user_date = models.Constraint(
        'UNIQUE(user_id, date)',
        'Det finns redan ett KEDS-test för denna användare och detta datum.',
    )

    @api.constrains('q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9')
    def _check_score_range(self):
        fields_list = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9']
        for rec in self:
            for f in fields_list:
                val = getattr(rec, f)
                if val < 0 or val > 6:
                    raise ValidationError(
                        f"Svar på fråga {f} måste vara mellan 0 och 6 (du angav {val})."
                    )
