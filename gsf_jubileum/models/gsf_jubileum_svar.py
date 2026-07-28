from odoo import api, fields, models

_FRAGOR = [
    (1,  "Öppning",          "Vilken tomt/fastighet gäller det, och vilket år kom familjen till Guldboda?"),
    (2,  "Ursprung",         "Vem köpte eller byggde stället, och varför just den platsen?"),
    (3,  "Släktträd",        "Vilka har bott eller vistats där? Berätta om generationer, namn och perioder."),
    (4,  "Huset och platsen","Har det skett ombyggnader eller gjorts speciella detaljer? Har tomten ett eget namn?"),
    (5,  "Musik",            "Finns det musik som förknippas med somrarna där?"),
    (6,  "Spel och böcker",  "Vilka sällskapsspel eller böcker hör ihop med stället?"),
    (7,  "Lekar och sport",  "Vilka lekar eller sporter är kopplade till tomten eller familjen?"),
    (8,  "En anekdot",       "Finns det en historia som alltid berättas när ni pratar om Guldboda?"),
    (9,  "Fritt utrymme",    "Är det något mer du vill ha med — något vi inte frågat om?"),
    (10, "Avslutning",       "Vill du bli kontaktad igen? Godkänner du att berättelsen kan publiceras i jubileumsskriften?"),
]

_FRAGA_SELECTION = [(str(nr), f"{nr}. {rubrik}") for nr, rubrik, _ in _FRAGOR]
_FRAGA_TEXT_MAP  = {nr: text for nr, _, text in _FRAGOR}


class GsfJubileumSvar(models.Model):
    _name = "gsf.jubileum.svar"
    _description = "GSF Jubileum — Svar per fråga"
    _order = "fastighet_id, fraga_nr"

    fastighet_id = fields.Many2one(
        "gsf.jubileum.fastighet",
        string="Fastighet",
        required=True,
        ondelete="cascade",
        index=True,
    )
    fraga_nr = fields.Selection(
        _FRAGA_SELECTION,
        string="Fråga",
    )
    fraga_text = fields.Char(
        string="Frågans lydelse",
        help="Fylls i automatiskt när du väljer fråga.",
    )
    svar_text = fields.Text(string="Svar")
    kalla = fields.Selection(
        [
            ("clio_chatt",         "Clio-chatt"),
            ("mejl",               "Mejl"),
            ("samtalsanteckning",  "Samtalsanteckning"),
        ],
        string="Källa",
    )

    @api.onchange("fraga_nr")
    def _onchange_fraga_nr(self):
        if self.fraga_nr:
            self.fraga_text = _FRAGA_TEXT_MAP.get(int(self.fraga_nr), "")
