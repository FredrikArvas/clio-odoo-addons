"""uap_classify_odoo.py — Claude-anrop för relevansklassificering inuti Odoo-processen."""

from __future__ import annotations

import json
import logging
import os
import re

_logger = logging.getLogger(__name__)

MODEL_SONNET = "claude-sonnet-4-6"
MAX_TOKENS = 2048

# Identisk med prompten i clio-tools/clio-uap/uap_classify.py — håll synkade.
_PROMPT_TEMPLATE = """Klassificera artiklarna nedan efter UAP-relevans.
Svara ENBART med en JSON-array: [{{"id": 123, "relevance_class": "confirmed"}}, ...]

Tillåtna värden:
  confirmed  - nämner kända fall: AARO, Grusch, Nimitz, GOFAST, GIMBAL, Rendlesham,
               UAP Congressional Hearings, Pentagon UFO
  likely     - UAP/UFO-observation med konkret kontext (plats, datum, vittne)
  uncertain  - nämner bara "UFO"/"UAP" utan specifik kontext
  off_topic  - spel, film, TV-serie, konsert, försäkring, resa - inget med UAP att göra

Artiklar:
{articles_json}
"""


def classify_records(records) -> None:
    try:
        import anthropic
    except ImportError:
        _logger.warning("[clio_uap] anthropic-paketet saknas i containern — avbryter")
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        _logger.warning("[clio_uap] ANTHROPIC_API_KEY saknas i miljön — avbryter")
        return

    rows = [
        {"id": r.id, "title": r.title or "", "snippet": (r.body_snippet or "")[:300]}
        for r in records
    ]
    prompt = _PROMPT_TEMPLATE.format(articles_json=json.dumps(rows, ensure_ascii=False))

    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(model=MODEL_SONNET, max_tokens=MAX_TOKENS,
                                      messages=[{"role": "user", "content": prompt}])
        raw = msg.content[0].text
    except Exception as e:
        _logger.warning("[clio_uap] Claude-anrop misslyckades: %s", e)
        return

    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        _logger.warning("[clio_uap] Inget JSON-block i svaret")
        return
    try:
        results = json.loads(match.group())
    except json.JSONDecodeError as e:
        _logger.warning("[clio_uap] JSON-parsning misslyckades: %s", e)
        return

    valid_ids = {r["id"] for r in rows}
    valid_classes = {"confirmed", "likely", "uncertain", "off_topic"}
    by_id = {r.id: r for r in records}
    for item in results:
        if item.get("id") in valid_ids and item.get("relevance_class") in valid_classes:
            by_id[item["id"]].relevance_class = item["relevance_class"]
