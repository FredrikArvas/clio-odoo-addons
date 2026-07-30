import json
import logging

import requests

from odoo import fields, http
from odoo.http import request

from ..fragor import FRAGOR

_logger = logging.getLogger(__name__)

BRIDGE_TIMEOUT = 45

BRIDGE_ERROR_MESSAGES = {
    "for_langt_meddelande": "Meddelandet var för långt — korta ner det lite och skicka igen.",
    "for_manga_turer": "Den här intervjun har nått sitt maxantal meddelanden. "
                        "Kontakta oss om du vill fortsätta.",
    "rate_limit": "Lite för många meddelanden på kort tid — vänta en liten stund och försök igen.",
}
GENERISKT_FEL = "AI-tjänsten är tillfälligt otillgänglig. Försök igen om en stund."


def _get_fastighet(token):
    if not token:
        return None
    return request.env["gsf.jubileum.fastighet"].sudo().search(
        [("unik_token", "=", token)], limit=1
    ) or None


def _bridge_call(path, payload):
    icp = request.env["ir.config_parameter"].sudo()
    url = icp.get_param("gsf.bridge.url", "http://172.19.0.1:8090")
    secret = icp.get_param("gsf.bridge.secret")
    if not secret:
        raise RuntimeError("gsf.bridge.secret saknas")
    resp = requests.post(
        f"{url}{path}",
        json=payload,
        headers={"X-Bridge-Secret": secret},
        timeout=BRIDGE_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


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
                    f"Vi kan se att fastigheten förvärvades {acquired.year} — berätta gärna "
                    f"hur familjen hittade till Guldboda! "
                    f"Vi tar det lugnt, en fråga i taget, och du kan alltid komma tillbaka "
                    f"via samma länk om du vill pausa."
                )
            else:
                opener = (
                    f"Hej och välkommen! Jag heter Clio och hjälper er att berätta om "
                    f"{fastighet.namn} till Guldboda Samfällighetsförenings 80-årsjubileum. "
                    f"Vi tar det lugnt, en fråga i taget — och du kan alltid komma tillbaka "
                    f"via samma länk om du vill pausa. "
                    f"Vi börjar från början: {FRAGOR[0][2]}"
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
        if fastighet.status in ("inlamnad", "vantar_godkannande",
                                "godkand_for_publicering", "vill_ej_publiceras"):
            return {"error": "Den här berättelsen är redan inlämnad."}

        message = (message or "").strip()
        if not message:
            return {"error": "Tomt meddelande."}

        history = json.loads(fastighet.coaching_history or "[]")

        acquired = fastighet.property_id.acquired_date if fastighet.property_id else None
        forvarvsdatum = str(acquired.year) if acquired else ""
        try:
            result = _bridge_call("/chat", {
                "fastighet_token": token,
                "namn": fastighet.namn,
                "forvarvsdatum": forvarvsdatum,
                "message": message,
                "fragor": FRAGOR,
                "history": history,
            })
        except Exception as e:
            _logger.error("gsf_jubileum bridge /chat error for token %s: %s", token, e)
            return {"error": GENERISKT_FEL}

        if result.get("error"):
            bridge_err = result["error"]
            _logger.warning("gsf_jubileum bridge /chat returned error %s for token %s",
                             bridge_err, token)
            return {"error": BRIDGE_ERROR_MESSAGES.get(bridge_err, GENERISKT_FEL)}

        reply = result.get("reply")
        if not reply:
            _logger.error("gsf_jubileum bridge /chat gave no reply for token %s", token)
            return {"error": GENERISKT_FEL}

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
        if fastighet.status in ("inlamnad", "vantar_godkannande", "godkand_for_publicering"):
            return {"ok": True, "already_submitted": True}
        if fastighet.status == "vill_ej_publiceras":
            return {"error": "Den här länken är inte längre aktiv."}

        samtycke = samtycke or {}
        godkand = bool(samtycke.get("godkand_publicering"))
        kontakt_igen = bool(samtycke.get("vill_bli_kontaktad_igen"))
        kommentar = (kommentar or samtycke.get("kommentar") or "").strip()

        history = json.loads(fastighet.coaching_history or "[]")
        SvarModel = request.env["gsf.jubileum.svar"].sudo()
        fastighet.svar_ids.unlink()

        svar_map = None
        try:
            result = _bridge_call("/extract", {
                "fastighet_token": token,
                "history": history,
                "fragor": FRAGOR,
            })
            svar_map = result.get("svar")
        except Exception as e:
            _logger.error("gsf_jubileum bridge /extract error for token %s: %s", token, e)

        # Extraktion misslyckad: lamna svar_ids tomt, redaktoren arbetar fran
        # coaching_history (ra-JSON) istallet for att aldrig blockera inlamningen.
        if svar_map:
            for nr, rubrik, fraga_text in FRAGOR:
                SvarModel.create({
                    "fastighet_id": fastighet.id,
                    "fraga_nr": str(nr),
                    "fraga_text": fraga_text,
                    "svar_text": svar_map.get(str(nr), "") or "",
                    "kalla": "clio_chatt",
                })

        SamtyckeModel = request.env["gsf.jubileum.samtycke"].sudo()
        fastighet.samtycke_ids.unlink()
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
