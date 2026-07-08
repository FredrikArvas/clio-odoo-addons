import json
import logging
import re
import urllib.error
import urllib.request

from odoo import fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)

_DEFAULT_URL = "http://172.18.0.1:7200"


def _service_url(env) -> str:
    return env["ir.config_parameter"].sudo().get_param(
        "clio.service.url", default=_DEFAULT_URL
    ).rstrip("/")


def _call(env, path: str, data: dict | None = None) -> dict:
    base = _service_url(env)
    url  = f"{base}{path}"
    body = json.dumps(data or {}).encode() if data is not None else None
    req  = urllib.request.Request(
        url, data=body,
        method="POST" if data is not None else "GET",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read())
    except urllib.error.URLError as e:
        raise UserError(f"Kunde inte nå clio-service ({base}): {e.reason}")
    except Exception as e:
        raise UserError(f"clio-service fel: {e}")
    if not result.get("ok"):
        raise UserError(result.get("error", "Okänt fel från clio-service"))
    return result


class ClioRag(models.TransientModel):
    _name        = "clio.rag"
    _description = "Clio RAG — Sökning"
    _rec_name    = "display_name"

    display_name = fields.Char(default="Clio RAG", readonly=True)

    rag_query  = fields.Char(string="Query")
    rag_mode   = fields.Selection(selection="_get_rag_modes", string="Source")
    rag_result = fields.Text(string="Answer", readonly=True)

    def _get_rag_modes(self):
        enabled = self.env["clio.rag.collection"].search([("enabled", "=", True)])
        return [(c.key, c.label) for c in enabled] or [("clio_books", "Böcker")]

    def action_rag_search(self):
        if not self.rag_query:
            raise UserError("Skriv en fråga först.")
        if not self.rag_mode:
            raise UserError("Välj en källa först.")
        result = _call(self.env, "/rag/query", {
            "q":          self.rag_query,
            "top":        5,
            "collection": self.rag_mode,
        })
        # Strippa markdown-formattering (** och *)
        answer = re.sub(r'\*\*(.+?)\*\*', r'\1', result.get("text", ""))
        answer = re.sub(r'\*(.+?)\*', r'\1', answer)

        sources = result.get("sources", [])
        if sources:
            # Deduplicera på (title, page_start, page_end)
            seen = set()
            unique = []
            for s in sources:
                key = (s.get("title"), s.get("page_start"), s.get("page_end"))
                if key not in seen:
                    seen.add(key)
                    unique.append(s)

            src_lines = ["\n─── Källor ───"]
            for s in unique:
                score = s.get("score", "")
                title = s.get("title", "?")
                if s.get("page_start"):
                    pages = f"s. {s['page_start']}"
                    if s.get("page_end") and s["page_end"] != s["page_start"]:
                        pages += f"–{s['page_end']}"
                    src_lines.append(f"  [{score}] {title}, {pages}")
                else:
                    url = s.get("url", "")
                    src_lines.append(f"  [{score}] {title}  {url}")
            answer += "\n".join(src_lines)
        self.rag_result = answer
        return self._reopen()

    def _reopen(self):
        res = {
            "type":      "ir.actions.act_window",
            "res_model": self._name,
            "res_id":    self.id,
            "view_mode": "form",
            "target":    "current",
        }
        view = self.env.ref("clio_rag.view_clio_rag_form", raise_if_not_found=False)
        if view:
            res["view_id"] = view.id
        return res
