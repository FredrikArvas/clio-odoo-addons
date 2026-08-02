# Gemensam frågelista — enda källan, används av både models och controllers.
FRAGOR = [
    (1,  "Öppning",          "Hur kom familjen till Guldboda — och vem var det som ursprungligen hittade hit?"),
    (2,  "Ursprung",         "Vem köpte eller byggde stället, och varför just den platsen?"),
    (3,  "Släktträd",        "Vilka har bott eller vistats där? Berätta om generationer, namn och perioder."),
    (4,  "Huset och platsen","Har det skett ombyggnader eller gjorts speciella detaljer? Har tomten ett eget namn?"),
    (5,  "Musik",            "Finns det musik som förknippas med somrarna där?"),
    (6,  "Spel och böcker",  "Vilka sällskapsspel eller böcker hör ihop med stället?"),
    (7,  "Lekar och sport",  "Vilka lekar eller sporter är kopplade till tomten eller familjen?"),
    (8,  "En anekdot",        "Finns det en historia som alltid berättas när ni pratar om Guldboda?"),
    (9,  "Ovanliga händelser","Har det hänt något ovanligt på tomten — oväntade besök, spöken eller händelser som familjen minns?"),
    (10, "Fritt utrymme",    "Är det något mer du vill ha med — något vi inte frågat om?"),
    (11, "Avslutning",       "Vill du bli kontaktad igen? Godkänner du att berättelsen kan publiceras i jubileumsskriften?"),
]


def fragor_text():
    return "\n".join(f"{nr}. {rubrik}: {text}" for nr, rubrik, text in FRAGOR)
