import uuid
from odoo import api, models, fields


class UapEncounter(models.Model):
    _name        = "uap.encounter"
    _inherit     = ["mail.thread"]
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

    # --- Transmorf-taxonomin (Projekt 23) ---
    is_case_report = fields.Boolean(
        string="Fallrapport",
        default=False,
        help="True om dokumentet beskriver ett faktiskt observationstillfälle/möte med UAP/fenomen.",
    )
    eth_origin = fields.Selection(
        selection=[
            ("0", "0 — Förklarat/mänskligt ursprung"),
            ("1", "1 — Troligen mänskligt, oklart"),
            ("2", "2 — Okänt ursprung"),
            ("3", "3 — Stark icke-mänsklig indikation"),
            ("4", "4 — Icke-mänsklig med officiell korroboration"),
            ("5", "5 — Bekräftat av declassificerade dokument"),
        ],
        string="ETH Origin",
        index=True,
    )
    craft_class = fields.Selection(
        selection=[
            ("I",       "I — Tetra"),
            ("II",      "II — Tic-Tac"),
            ("III",     "III — Blob"),
            ("IV",      "IV — Beam"),
            ("V",       "V — Manta-Ray"),
            ("VI",      "VI — Bright-Star"),
            ("VII",     "VII — Jellyfish"),
            ("VIII",    "VIII — Hornet"),
            ("IX",      "IX — Egg"),
            ("X",       "X — Teardrop"),
            ("unknown", "Unknown"),
        ],
        string="Craft Class (Skywatcher)",
    )
    entity_type = fields.Selection(
        selection=[
            # --- Modern UAP-taxonomi ---
            ("Nordic",      "Nordic"),
            ("TallGray",    "TallGray"),
            ("ShortGray",   "ShortGray"),
            ("LongGray",    "LongGray"),
            ("Reptilian",   "Reptilian"),
            ("Mantid",      "Mantid"),
            ("Hybrid",      "Hybrid"),
            ("Energy",      "Energy"),
            # --- Transmorf-taxonomi: bibliska/historiska entiteter ---
            ("Angel",       "Angel (mal'ak)"),
            ("AngelOfLord", "Angel of the LORD (teofani)"),
            ("Cherub",      "Cherubim"),
            ("Seraph",      "Seraphim"),
            ("Nephilim",    "Nephilim / Giant"),
            ("Demon",       "Demon / Evil Spirit"),
            # --- Obestämd ---
            ("Unknown",     "Unknown"),
        ],
        string="Entity Type",
    )
    intelligence_indicator = fields.Selection(
        selection=[
            ("0", "0 — Inga tecken på intelligens"),
            ("1", "1 — Möjlig reaktiv/avsiktlig rörelse"),
            ("2", "2 — Tydlig intelligens"),
            ("3", "3 — Direkt kontakt eller kommunikation"),
        ],
        string="Intelligence Indicator",
    )
    suppression_indicator = fields.Boolean(
        string="Suppression Indicator",
        default=False,
        help="Texten tonar ned eller undviker ETH-implikationer trots eth_origin >= 3.",
    )
    suppression_note = fields.Char(
        string="Suppression Note",
        size=120,
    )
    afu_article_id = fields.Integer(
        string="AFU Article ID",
        help="Odoo-ID för källartikeln i clio.media.article (uap-databasen).",
        index=True,
    )
    afu_doc_path = fields.Char(
        string="AFU Document Path",
        help="Relativ sökväg till källdokumentet under data/downloads/.",
        index=True,
    )

    # --- Övrigt ---
    research_notes = fields.Text(string="Research Notes")
    # --- Transmorf-taxonomin (Projekt 23) ---
    is_case_report = fields.Boolean(
        string="Fallrapport", default=False,
        help="True om dokumentet innehåller ett konkret fallrapport enligt transmorf-taxonomin",
        index=True,
    )
    eth_origin = fields.Selection(
        selection=[
            ("0", "0 — Förklarat/mänskligt ursprung"),
            ("1", "1 — Troligen mänskligt, oklart"),
            ("2", "2 — Okänt ursprung"),
            ("3", "3 — Stark icke-mänsklig indikation"),
            ("4", "4 — Icke-mänsklig med officiell korroboration"),
            ("5", "5 — Bekräftat av declassificerade dokument"),
        ],
        string="ETH Origin", index=True,
    )
    craft_class = fields.Selection(
        selection=[
            ("I",   "I — Tetra"),
            ("II",  "II — Tic-Tac"),
            ("III", "III — Blob"),
            ("IV",  "IV — Beam"),
            ("V",   "V — Manta-Ray"),
            ("VI",  "VI — Bright-Star"),
            ("VII", "VII — Jellyfish"),
            ("VIII","VIII — Hornet"),
            ("IX",  "IX — Egg"),
            ("X",   "X — Teardrop"),
            ("unknown", "Unknown"),
        ],
        string="Craft Class (Skywatcher)",
    )
    entity_type = fields.Selection(
        selection=[
            ("Nordic",    "Nordic"),
            ("TallGray",  "TallGray"),
            ("ShortGray", "ShortGray"),
            ("LongGray",  "LongGray"),
            ("Reptilian", "Reptilian"),
            ("Mantid",    "Mantid"),
            ("Hybrid",    "Hybrid"),
            ("Energy",    "Energy"),
            ("Angel",       "Angel (mal'ak)"),
            ("AngelOfLord", "Angel of the LORD (teofani)"),
            ("Cherub",      "Cherubim"),
            ("Seraph",      "Seraphim"),
            ("Nephilim",    "Nephilim / Giant"),
            ("Unknown",     "Unknown"),
        ],
        string="Entity Type",
    )
    suppression_indicator = fields.Boolean(
        string="Suppression Indicator", default=False,
        help="Tecken på aktivt undertryckande av information",
    )
    suppression_note = fields.Char(string="Suppression Note", size=120)
    afu_article_id = fields.Integer(
        string="AFU Article ID",
        help="Ersatt av article_ids (Källdokument) — behålls för spårbarhet. "
             "Odoo-ID för källartikeln i clio.media.article",
        index=True,
    )
    afu_doc_path = fields.Char(
        string="AFU Document Path",
        help="Relativ sökväg till källdokumentet under data/downloads/",
        index=True,
    )
    # Källdokument: en händelse kan ha flera dokument (skanning, översättning,
    # flera sidor) och ett dokument kan beskriva flera händelser.
    article_ids = fields.Many2many(
        comodel_name="clio.media.article",
        relation="uap_encounter_article_rel",
        column1="encounter_id",
        column2="article_id",
        string="Källdokument",
    )
    article_count = fields.Integer(
        string="# Källdokument",
        compute="_compute_article_count",
    )

    neo4j_node_id = fields.Char(string="Neo4j Node ID", readonly=True, copy=False)
    passage_ids = fields.One2many(
        comodel_name="uap.encounter.passage",
        inverse_name="encounter_id",
        string="Passager",
    )
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

    def _compute_counts(self):
        for rec in self:
            rec.source_count = len(rec.source_ids)
            rec.witness_count = len(rec.witness_ids)
            rec.verification_count = len(rec.verification_ids)
            rec.classification_count = len(rec.classification_ids)
            rec.anomaly_count = len(rec.anomaly_ids)

    @api.model_create_multi
    def create(self, vals_list):
        # Encounters importeras i bulk (NUFORC, GEIPAN, AFU …) — ingen följare
        # eller "skapad"-logg per post; chattern är till för kommentarer.
        return super(
            UapEncounter,
            self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True),
        ).create(vals_list)

    def _compute_article_count(self):
        for rec in self:
            rec.article_count = len(rec.article_ids)

    def action_open_articles(self):
        self.ensure_one()
        return {
            "type":      "ir.actions.act_window",
            "name":      "Källdokument",
            "res_model": "clio.media.article",
            "view_mode": "list,form",
            "domain":    [("id", "in", self.article_ids.ids)],
            "context":   {"create": False},
        }

    def _compute_observables_count(self):
        obs_fields = [
            "obs_antigravity", "obs_instant_accel", "obs_hypersonic",
            "obs_low_observability", "obs_transmedium",
        ]
        for rec in self:
            rec.observables_count = sum(1 for f in obs_fields if getattr(rec, f))
