import json
import logging

from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)

FRAGOR = [
    (1,  "Öppning",         "Hur kom familjen till Guldboda — och vem var det som ursprungligen hittade hit?"),
    (2,  "Ursprung",        "Vem köpte eller byggde stället, och varför just den platsen?"),
    (3,  "Släktträd",       "Vilka har bott eller vistats där? Berätta om generationer, namn och perioder."),
    (4,  "Huset och platsen","Har det skett ombyggnader eller gjorts speciella detaljer? Har tomten ett eget namn?"),
    (5,  "Musik",           "Finns det musik som förknippas med somrarna där?"),
    (6,  "Spel och böcker", "Vilka sällskapsspel eller böcker hör ihop med stället?"),
    (7,  "Lekar och sport", "Vilka lekar eller sporter är kopplade till tomten eller familjen?"),
    (8,  "En anekdot",      "Finns det en historia som alltid berättas när ni pratar om Guldboda?"),
    (9,  "Fritt utrymme",   "Är det något mer du vill ha med — något vi inte frågat om?"),
    (10, "Avslutning",      "Vill du bli kontaktad igen? Godkänner du att berättelsen kan publiceras i jubileumsskriften?"),
]

SYSTEM_PROMPT_TEMPLATE = """\
Du är Clio, en varm och nyfiken intervjuare som hjälper familjer i Guldboda \
att berätta sin fastighetshistoria till GSF:s 80-årsjubileumsskrift.

Känd information om fastigheten:
- Beteckning: {namn}
- Förvärvsdatum: {forvarvsdatum}

Använd denna information aktivt — fråga inte om saker du redan vet.

Ditt uppdrag är att ställa nedanstående 10 frågor i naturlig, följsam ordning — \
inte som ett stelbent formulär. Lyssna aktivt, ställ gärna en spontan följdfråga \
om något är intressant, och hjälp familjen att formulera minnen i ord.

Frågelista (ställ dem ungefärligt i denna ordning):
{fragor}

Regler:
- Svara alltid på svenska.
- En fråga (eller kortare uppföljning) per svar — överskölj aldrig med flera frågor.
- Håll tonen varm, nyfiken och respektfull.
- Fråga 10 handlar om samtycke — ställ den mot slutet och formulera den tydligt.
- Skriv inte berättelsen åt familjen — coacha dem att berätta själva.
- När alla 10 frågor är besvarade (eller familjen signalerar att de är klara): \
avsluta med en kort summering och en instruktion att klicka på "Skicka in".\
"""


def _fragor_text():
    return "\n".join(f"{nr}. {rubrik}: {text}" for nr, rubrik, text in FRAGOR)


def _get_fastighet(token):
    if not token:
        return None
    return request.env["gsf.jubileum.fastighet"].sudo().search(
        [("unik_token", "=", token)], limit=1
    ) or None


class GsfJubileumPortal(http.Controller):

    @http.route("/jubileum/hamta-lank", type="http", auth="public", website=True,
                methods=["GET", "POST"])
    def hamta_lank(self, **post):
        sent = False
        if request.httprequest.method == "POST":
            email = (post.get("email") or "").strip()
            if email:
                request.env["gsf.jubileum.fastighet"].sudo().skicka_lank_for_email(email)
            sent = True
        return request.render("gsf_jubileum.page_hamta_lank", {"sent": sent})


    @http.route("/jubileum/<string:token>", type="http", auth="public", website=True)
    def jubileum_index(self, token, **kw):
        fastighet = _get_fastighet(token)
        if not fastighet:
            return request.not_found()
        if fastighet.status == "vill_ej_publiceras":
            return request.render("gsf_jubileum.page_already_closed", {"fastighet": fastighet})

        history = json.loads(fastighet.coaching_history or "[]")

        if not history:
            acquired = fastighet.property_id.acquired_date if fastighet.property_id else None
            if acquired:
                opener = (
                    f"Hej och välkommen! Jag heter Clio och hjälper er att berätta om "
                    f"{fastighet.namn} till Guldboda Samfällighetsförenings 80-årsjubileum. "
                    f"Vi kan se att fastigheten förvärvades {acquired.year} — berätta gärna hur familjen hittade till Guldboda! "
                    f"Vi tar det lugnt, en fråga i taget, och du kan alltid komma tillbaka via samma länk om du vill pausa."
                )
            else:
                opener = (
                    f"Hej och välkommen! Jag heter Clio och hjälper er att berätta om "
                    f"{fastighet.namn} till Guldboda Samfällighetsförenings 80-årsjubileum. "
                    f"Vi tar det lugnt, en fråga i taget — och du kan alltid komma tillbaka "
                    f"via samma länk om du vill pausa. "
                    f"Vi börjar från början: Vilket år kom familjen till Guldboda, och vem var det som ursprungligen hittade hit?"
                )
            history = [{"role": "assistant", "content": opener}]
            fastighet.write({"coaching_history": json.dumps(history, ensure_ascii=False)})

        inlamnad = fastighet.status in ("inlamnad", "vantar_godkannande",
                                        "godkand_for_publicering", "vill_ej_publiceras")
        return request.render("gsf_jubileum.page_interview", {
            "fastighet": fastighet,
            "token": token,
            "history": history,
            "inlamnad": inlamnad,
        })

    @http.route("/jubileum/<string:token>/chat", type="jsonrpc", auth="public")
    def jubileum_chat(self, token, message="", **kw):
        fastighet = _get_fastighet(token)
        if not fastighet:
            return {"error": "Ogiltig länk."}
        if fastighet.status in ("inlamnad", "godkand_for_publicering", "vill_ej_publiceras"):
            return {"error": "Den här berättelsen är redan inlämnad."}

        message = (message or "").strip()
        if not message:
            return {"error": "Tomt meddelande."}

        history = json.loads(fastighet.coaching_history or "[]")

        try:
            import anthropic
            api_key = (
                request.env["ir.config_parameter"].sudo().get_param("gsf.anthropic.api_key")
                or request.env["ir.config_parameter"].sudo().get_param("clio.anthropic.api_key")
            )
            if not api_key:
                return {"error": "API-nyckel saknas — kontakta Fredrik."}

            acquired = fastighet.property_id.acquired_date if fastighet.property_id else None
            forvarvsdatum = str(acquired.year) if acquired else "okänt"
            system = SYSTEM_PROMPT_TEMPLATE.format(
                namn=fastighet.namn,
                forvarvsdatum=forvarvsdatum,
                fragor=_fragor_text(),
            )
            api_messages = history + [{"role": "user", "content": message}]
            if api_messages[0]["role"] != "user":
                api_messages = [{"role": "user", "content": "[start]"}] + api_messages

            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=600,
                system=system,
                messages=api_messages,
            )
            reply = response.content[0].text

        except Exception as e:
            _logger.error("gsf_jubileum chat error for token %s: %s", token, e)
            return {"error": "AI-tjänsten är tillfälligt otillgänglig. Försök igen om en stund."}

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})

        new_status = "paborjad" if fastighet.status in ("ej_kontaktad", "inbjuden") else fastighet.status
        fastighet.write({
            "coaching_history": json.dumps(history, ensure_ascii=False),
            "status": new_status,
            "kanal": "clio_chatt",
        })
        return {"reply": reply}

    @http.route("/jubileum/<string:token>/submit", type="jsonrpc", auth="public")
    def jubileum_submit(self, token, samtycke=None, kommentar="", **kw):
        fastighet = _get_fastighet(token)
        if not fastighet:
            return {"error": "Ogiltig länk."}
        if fastighet.status in ("inlamnad", "godkand_for_publicering"):
            return {"ok": True, "already_submitted": True}

        samtycke = samtycke or {}
        godkand = bool(samtycke.get("godkand_publicering"))
        kontakt_igen = bool(samtycke.get("vill_bli_kontaktad_igen"))
        kommentar = (kommentar or samtycke.get("kommentar") or "").strip()

        history = json.loads(fastighet.coaching_history or "[]")
        SvarModel = request.env["gsf.jubileum.svar"].sudo()
        fastighet.svar_ids.unlink()

        # Para ihop user-svar med frågor i ordning (Clio frågar 1–10 sekventiellt)
        user_messages = [m["content"] for m in history if m["role"] == "user"]
        for idx, (nr, rubrik, fraga_text) in enumerate(FRAGOR):
            SvarModel.create({
                "fastighet_id": fastighet.id,
                "fraga_nr": str(nr),
                "fraga_text": fraga_text,
                "svar_text": user_messages[idx] if idx < len(user_messages) else "",
                "kalla": "clio_chatt",
            })

        SamtyckeModel = request.env["gsf.jubileum.samtycke"].sudo()
        fastighet.samtycke_id.unlink()
        SamtyckeModel.create({
            "fastighet_id": fastighet.id,
            "godkand_publicering": godkand,
            "vill_bli_kontaktad_igen": kontakt_igen,
            "kommentar": kommentar,
        })

        new_status = "vill_ej_publiceras" if not godkand else "inlamnad"
        fastighet.write({
            "status": new_status,
            "datum_inlamnad": fields.Date.today(),
        })
        return {"ok": True}


