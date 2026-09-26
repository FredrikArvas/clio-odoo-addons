from odoo import models, fields, api


class UapEncounterClassification(models.Model):
    _name        = "uap.encounter.classification"
    _description = "UAP — Encounter Classification"
    _order       = "system, class_value"
    _rec_name    = "label"

    encounter_id = fields.Many2one(
        comodel_name="uap.encounter",
        string="Encounter",
        required=True,
        ondelete="cascade",
        index=True,
    )
    system = fields.Selection(
        selection=[
            ("skywatcher",       "Skywatcher I–X"),
            ("transmorf_entity", "Transmorf — Varelse"),
            ("hynek",            "Hynek CE"),
            ("eth",              "ETH-ursprung"),
            ("custom",           "Anpassad"),
        ],
        string="System",
        required=True,
        index=True,
    )
    class_value = fields.Char(
        string="Klass",
        required=True,
        help="Klassens nyckel: t.ex. III (Skywatcher), Short Gray (Transmorf), CE2 (Hynek), 4 (ETH)",
    )
    label = fields.Char(
        string="Etikett",
        help="Läsbar etikett: t.ex. 'III — Blob', 'Short Gray', 'CE2 — Physical Trace'",
    )
    transmorf_entity_id = fields.Many2one(
        comodel_name="uap.transmorf.entity",
        string="Transmorf-entitet",
        ondelete="set null",
        index=True,
        help="Länk till entitetsregistret — fylls i när system = Transmorf — Varelse",
    )
    confidence = fields.Selection(
        selection=[
            ("auto_high", "Auto — hög"),
            ("auto_low",  "Auto — låg"),
            ("manual",    "Manuell"),
        ],
        string="Konfidensgrad",
    )
    source = fields.Selection(
        selection=[
            ("auto_shape", "Auto (shape-mappning)"),
            ("auto_llm",   "Auto (LLM)"),
            ("manual",     "Manuell granskning"),
        ],
        string="Källa",
    )
    notes = fields.Text(string="Noteringar")
    classified_at = fields.Datetime(
        string="Klassificerad",
        default=fields.Datetime.now,
    )

    @api.onchange("system", "class_value", "transmorf_entity_id")
    def _onchange_fill_label(self):
        skywatcher_labels = {
            "I":    "I — Tetra",
            "II":   "II — Tic Tac",
            "III":  "III — Blob",
            "IV":   "IV — Beam",
            "V":    "V — Manta Ray",
            "VI":   "VI — Bright Star",
            "VII":  "VII — Jellyfish",
            "VIII": "VIII — Hornet",
            "IX":   "IX — Egg",
            "X":    "X — Teardrop",
        }
        eth_labels = {
            "0": "0 — Förklarat",
            "1": "1 — Oklart",
            "2": "2 — Troligt mänskligt",
            "3": "3 — Okänt ursprung",
            "4": "4 — Troligt icke-mänskligt",
            "5": "5 — Bekräftat icke-mänskligt",
        }
        if self.system == "skywatcher" and self.class_value in skywatcher_labels:
            self.label = skywatcher_labels[self.class_value]
        elif self.system == "eth" and self.class_value in eth_labels:
            self.label = eth_labels[self.class_value]
        elif self.system == "transmorf_entity" and self.transmorf_entity_id:
            self.label = self.transmorf_entity_id.name
            if not self.class_value:
                self.class_value = self.transmorf_entity_id.name
        elif self.class_value and not self.label:
            self.label = self.class_value
