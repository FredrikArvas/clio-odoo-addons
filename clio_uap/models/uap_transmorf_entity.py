from odoo import models, fields, api


class UapTransmorfEntity(models.Model):
    _name        = "uap.transmorf.entity"
    _description = "Transmorf — Entitetsregister"
    _order       = "category, name"
    _rec_name    = "name"

    name = fields.Char(string="Beteckning", required=True, index=True)
    category = fields.Selection(
        selection=[
            ("varelse",  "Varelse"),
            ("farkost",  "Farkost"),
            ("energi",   "Energivarelse"),
            ("hybrid",   "Hybrid"),
            ("okand",    "Okänd"),
        ],
        string="Kategori",
        required=True,
        index=True,
        default="varelse",
    )

    # --- Linnésk taxonomi (alla 7 nivåer) ---
    domain_taxon  = fields.Char(string="Domän",   help="t.ex. Eukaryota, Bacteria")
    kingdom_taxon = fields.Char(string="Rike",    help="t.ex. Animalia, Fungi")
    phylum_taxon  = fields.Char(string="Stam",    help="t.ex. Chordata, Arthropoda")
    class_taxon   = fields.Char(string="Klass",   help="t.ex. Mammalia, Insecta, Reptilia")
    order_taxon   = fields.Char(string="Ordning", help="t.ex. Primates, Carnivora")
    family_taxon  = fields.Char(string="Familj",  help="t.ex. Hominidae, Felidae")
    genus_taxon   = fields.Char(string="Släkte",  help="t.ex. Homo, Pan")
    species_taxon = fields.Char(string="Art",     help="t.ex. H. nordicus, Short Gray")

    # --- Medium / rörlighet ---
    medium_aerial      = fields.Boolean(string="Aerisk (luft)")
    medium_aquatic     = fields.Boolean(string="Aquatisk (vatten)")
    medium_space       = fields.Boolean(string="Rymd")
    medium_terrestrial = fields.Boolean(string="Terrestriell (mark)")
    medium_among_us    = fields.Boolean(string="Bland oss (undantagen perception)")
    medium_transmedium = fields.Boolean(string="Transmedium (byter medium)")

    # --- Biologisk status ---
    biological_status = fields.Selection(
        selection=[
            ("biological",  "Biologisk"),
            ("constructed", "Konstruerad / teknologisk"),
            ("hybrid",      "Hybrid (bio + teknologi)"),
            ("energetic",   "Energibaserad / icke-korporeal"),
            ("unknown",     "Okänd"),
        ],
        string="Biologisk status",
        default="unknown",
    )

    # --- Bedömning ---
    confidence = fields.Selection(
        selection=[
            ("0", "0 — Spekulativ / inga primärkällor"),
            ("1", "1 — Enskild rapport"),
            ("2", "2 — Flera oberoende rapporter"),
            ("3", "3 — Fysisk evidens"),
            ("4", "4 — Officiellt erkänd / program"),
            ("5", "5 — Bekräftat / declassified"),
        ],
        string="Konfidensgrad",
        default="1",
    )

    morphology = fields.Text(
        string="Morfologi",
        help="Utseende, storlek, anatomi, särdrag",
    )
    notes = fields.Text(string="Anteckningar / källor")

    # --- Relationer ---
    classification_ids = fields.One2many(
        comodel_name="uap.encounter.classification",
        inverse_name="transmorf_entity_id",
        string="Klassificeringar",
    )
    encounter_count = fields.Integer(
        string="# Encounters",
        compute="_compute_encounter_count",
        store=False,
    )

    @api.depends("classification_ids")
    def _compute_encounter_count(self):
        for rec in self:
            rec.encounter_count = len(rec.classification_ids.mapped("encounter_id"))
