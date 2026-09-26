import uuid
from odoo import models, fields


class UapEncounter(models.Model):
    _name        = "uap.encounter"
    _description = "UAP — Encounter"
    _order       = "date_observed desc, encounter_id"
    _rec_name    = "title_en"

    encounter_id = fields.Char(
        string="Encounter ID",
        required=True,
        index=True,
        help="Unikt text-ID, t.ex. SWE_PPXL_0001",
    )
    encounter_guid = fields.Char(
        string="GUID",
        readonly=True,
        default=lambda self: str(uuid.uuid4()),
        copy=False,
    )

    # --- Tid & plats ---
    date_observed = fields.Datetime(string="Date Observed")
    country_id = fields.Many2one(
        comodel_name="res.country",
        string="Country",
        index=True,
    )
    location = fields.Text(string="Location")

    # --- Titlar ---
    title_en = fields.Char(string="Title (EN)")
    title_original = fields.Char(string="Title (Original)")

    # --- Beskrivningar ---
    description_en = fields.Text(string="Description (EN)")
    description_sv = fields.Text(string="Description (SV)")
    description_original = fields.Text(string="Description (Original)")
    language_original = fields.Selection(
        selection=[
            ("en",    "English"),
            ("sv",    "Swedish"),
            ("pt",    "Portuguese"),
            ("es",    "Spanish"),
            ("fr",    "French"),
            ("de",    "German"),
            ("ja",    "Japanese"),
            ("other", "Other"),
        ],
        string="Original Language",
    )

    # --- Klassificering ---
    encounter_class = fields.Selection(
        selection=[
            ("1", "1 — Sighting"),
            ("2", "2 — Close Encounter"),
            ("3", "3 — Physical Evidence"),
            ("4", "4 — Abduction / Contact"),
            ("5", "5 — Media / Cultural Reference"),
        ],
        string="Encounter Class",
        index=True,
    )
    discourse_level = fields.Selection(
        selection=[
            ("1", "1 — Fringe / Unknown"),
            ("2", "2 — Limited Public Awareness"),
            ("3", "3 — Active Public Debate"),
            ("4", "4 — Official Acknowledgement"),
            ("5", "5 — Confirmed / Declassified"),
        ],
        string="Discourse Level",
        index=True,
    )
    official_response = fields.Selection(
        selection=[
            ("A", "A — No Response"),
            ("B", "B — Denial"),
            ("C", "C — Acknowledgement"),
            ("D", "D — Investigation"),
            ("E", "E — Confirmation"),
        ],
        string="Official Response",
    )
    status = fields.Selection(
        selection=[
            ("pending",  "Pending Review"),
            ("verified", "Verified"),
            ("archived", "Archived"),
        ],
        string="Status",
        default="pending",
        index=True,
    )

    # --- Skywatcher-klassificering (deprecated: se classification_ids) ---
    skywatcher_class = fields.Selection(
        selection=[
            ("I",    "I — Tetra"),
            ("II",   "II — Tic Tac"),
            ("III",  "III — Blob"),
            ("IV",   "IV — Beam"),
            ("V",    "V — Manta Ray"),
            ("VI",   "VI — Bright Star"),
            ("VII",  "VII — Jellyfish"),
            ("VIII", "VIII — Hornet"),
            ("IX",   "IX — Egg"),
            ("X",    "X — Teardrop"),
        ],
        string="Skywatcher Class",
        index=True,
        help="Morfologisk klass enligt Skywatcher UAP Classification Guide (I-IX + X Teardrop)",
    )
    skywatcher_confidence = fields.Selection(
        selection=[
            ("auto_high", "Auto — hög"),
            ("auto_low",  "Auto — låg"),
            ("manual",    "Manuell"),
        ],
        string="SW Confidence",
        help="Källan till Skywatcher-klassificeringen: automatisk (hög/låg) eller manuell granskning",
    )
    skywatcher_notes = fields.Text(
        string="SW Notes",
        help="Motivering eller kommentar till Skywatcher-klassificeringen",
    )

    # --- Relationer ---
    source_ids = fields.Many2many(
        comodel_name="uap.source",
        relation="uap_encounter_source_rel",
        column1="encounter_id_col",
        column2="source_id_col",
        string="Sources",
    )
    witness_ids = fields.Many2many(
        comodel_name="uap.witness",
        relation="uap_encounter_witness_rel",
        column1="encounter_id_col",
        column2="witness_id_col",
        string="Witnesses",
    )
    verification_ids = fields.One2many(
        comodel_name="uap.verification",
        inverse_name="encounter_id",
        string="Verification Log",
    )
    classification_ids = fields.One2many(
        comodel_name="uap.encounter.classification",
        inverse_name="encounter_id",
        string="Klassificeringar",
    )
    anomaly_ids = fields.Many2many(
        comodel_name="uap.anomaly",
        relation="uap_anomaly_encounter_rel",
        column1="encounter_id",
        column2="anomaly_id",
        string="Anomalier",
    )

    # --- ETH-hypotes (utomjordiskt ursprung) ---
    eth_origin = fields.Selection(
        selection=[
            ("0", "0 — Förklarat / Explained"),
            ("1", "1 — Oklart / Unclear"),
            ("2", "2 — Troligt mänskligt / Likely Human"),
            ("3", "3 — Okänt ursprung / Unknown Origin"),
            ("4", "4 — Troligt icke-mänskligt / Likely Non-Human"),
            ("5", "5 — Bekräftat icke-mänskligt / Confirmed Non-Human"),
        ],
        string="ETH Origin",
        index=True,
        help="Bedömning av icke-mänskligt / utomjordiskt ursprung (0=Förklarat, 5=Bekräftat)",
    )
    intelligence_indicator = fields.Selection(
        selection=[
            ("0", "0 — Inga tecken / No Signs"),
            ("1", "1 — Svaga tecken / Weak Signs"),
            ("2", "2 — Tydliga tecken / Clear Signs"),
            ("3", "3 — Direkt kontakt / Direct Contact"),
        ],
        string="Intelligence Indicator",
        help="Tecken på intelligent kontroll (0=Inga, 3=Direkt kontakt/besättning observerad)",
    )

    # --- Pentagon Five Observables (AARO) ---
    obs_antigravity = fields.Boolean(
        string="Anti-Gravity",
        default=False,
        help="Observatorn rapporterar rörelse utan synbara propulsionssystem",
    )
    obs_instant_accel = fields.Boolean(
        string="Instant Acceleration",
        default=False,
        help="Omedelbar acceleration / riktningsändring bortom känd fysik",
    )
    obs_hypersonic = fields.Boolean(
        string="Hypersonic",
        default=False,
        help="Hypersonisk hastighet utan värmesignatur",
    )
    obs_low_observability = fields.Boolean(
        string="Low Observability",
        default=False,
        help="Låg observerbarhet / stealth-förmåga",
    )
    obs_transmedium = fields.Boolean(
        string="Trans-Medium",
        default=False,
        help="Rör sig obehindrat mellan luft, vatten och rymden",
    )
    observables_count = fields.Integer(
        string="Observables",
        compute="_compute_observables_count",
        store=True,
        help="Antal Pentagon Five Observables som rapporterats (0-5)",
    )

    # --- Övrigt ---
    research_notes = fields.Text(string="Research Notes")
    neo4j_node_id = fields.Char(string="Neo4j Node ID", readonly=True, copy=False)
    series_id = fields.Many2one("uap.series", string="Series", index=True, ondelete="set null")
    database_id = fields.Many2one("uap.database", string="Source Database", index=True, ondelete="set null")

    # --- Computed counts för smartbuttons ---
    source_count = fields.Integer(
        string="# Sources",
        compute="_compute_counts",
        store=False,
    )
    witness_count = fields.Integer(
        string="# Witnesses",
        compute="_compute_counts",
        store=False,
    )
    verification_count = fields.Integer(
        string="# Verifications",
        compute="_compute_counts",
        store=False,
    )
    classification_count = fields.Integer(
        string="# Klassificeringar",
        compute="_compute_counts",
        store=False,
    )
    anomaly_count = fields.Integer(
        string="# Anomalier",
        compute="_compute_counts",
        store=False,
    )

    def _compute_counts(self):
        for rec in self:
            rec.source_count = len(rec.source_ids)
            rec.witness_count = len(rec.witness_ids)
            rec.verification_count = len(rec.verification_ids)
            rec.classification_count = len(rec.classification_ids)
            rec.anomaly_count = len(rec.anomaly_ids)

    def _compute_observables_count(self):
        obs_fields = [
            "obs_antigravity", "obs_instant_accel", "obs_hypersonic",
            "obs_low_observability", "obs_transmedium",
        ]
        for rec in self:
            rec.observables_count = sum(1 for f in obs_fields if getattr(rec, f))
