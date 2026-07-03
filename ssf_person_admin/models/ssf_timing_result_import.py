import base64
import csv
import io

from odoo import fields, models

CHIP_HEADERS = {"chipnummer", "chip", "chipno", "chipnr", "bricka", "chip nr", "chip-nummer"}
RANK_HEADERS = {"placering", "rank", "plac"}
TIME_HEADERS = {"tid", "time"}
STATUS_HEADERS = {"status"}


def _normalize(value):
    return (value or "").strip().lower()


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


class SsfTimingResultImport(models.TransientModel):
    _name        = "ssf.timing.result.import"
    _description = "SSFTiming-resultatimport"

    competition_id = fields.Many2one(
        "ssf.competition", string="Tavling", required=True,
    )
    file = fields.Binary(string="Resultatfil", required=True)
    filename = fields.Char(string="Filnamn")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Klar")],
        default="draft", readonly=True,
    )
    result_summary = fields.Text(string="Sammanfattning", readonly=True)

    def _parse_rows(self):
        raw = base64.b64decode(self.file)
        text = raw.decode("utf-8-sig")
        sample = text[:2048]
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=";,")
        except csv.Error:
            dialect = csv.excel
            dialect.delimiter = ";"
        reader = csv.DictReader(io.StringIO(text), dialect=dialect)
        rows = []
        for raw_row in reader:
            row = {_normalize(k): (v or "").strip() for k, v in raw_row.items() if k}
            rows.append(row)
        return rows

    @staticmethod
    def _pick(row, headers):
        for key in row:
            if key in headers:
                return row[key]
        return ""

    def action_import(self):
        self.ensure_one()
        comp = self.competition_id
        rows = self._parse_rows()

        created = updated = skipped_ssfta = unmatched_chip = unmatched_entry = 0
        unmatched_chip_values = []

        for row in rows:
            chip_no = self._pick(row, CHIP_HEADERS)
            if not chip_no:
                continue
            chip = self.env["ssf.person.chip"].search([("chip_no", "=", chip_no)], limit=1)
            if not chip or not chip.partner_id:
                unmatched_chip += 1
                unmatched_chip_values.append(chip_no)
                continue

            entry = self.env["ssf.entry"].search([
                ("competition_id", "=", comp.id),
                ("person_id", "=", chip.partner_id.id),
            ], limit=1)
            if not entry or not entry.ccd_id:
                unmatched_entry += 1
                continue

            ccd = entry.ccd_id
            result_list = self.env["ssf.result.list"].search(
                [("ccd_id", "=", ccd.id)], limit=1,
            )
            if not result_list:
                result_list = self.env["ssf.result.list"].create({
                    "ccd_id": ccd.id,
                    "source": "ssftiming",
                    "class_name": ccd.class_id.name if ccd.class_id else "",
                    "discipline_name": ccd.discipline_id.name if ccd.discipline_id else "",
                })

            result = self.env["ssf.result"].search([
                ("result_list_id", "=", result_list.id),
                ("person_id", "=", chip.partner_id.id),
            ], limit=1)

            if result and result.source == "ssfta":
                skipped_ssfta += 1
                continue

            person = chip.partner_id
            parts = (person.name or "").split(" ", 1)
            vals = {
                "result_list_id": result_list.id,
                "person_id": person.id,
                "rank": _to_int(self._pick(row, RANK_HEADERS)),
                "time": self._pick(row, TIME_HEADERS),
                "status": self._pick(row, STATUS_HEADERS),
                "firstname": parts[0] if parts else "",
                "lastname": parts[1] if len(parts) > 1 else "",
                "birth_year": person.birthdate_date.year if person.birthdate_date else 0,
                "source": "ssftiming",
            }
            if result:
                result.write(vals)
                updated += 1
            else:
                self.env["ssf.result"].create(vals)
                created += 1

        summary_lines = [
            "Skapade: {}".format(created),
            "Uppdaterade: {}".format(updated),
            "Hoppade over (redan SSFTA-resultat): {}".format(skipped_ssfta),
            "Ej matchade chip: {}".format(unmatched_chip),
            "Matchade chip utan anmalan i tavlingen: {}".format(unmatched_entry),
        ]
        if unmatched_chip_values:
            summary_lines.append("Okanda chip-nummer: " + ", ".join(unmatched_chip_values[:50]))

        self.write({
            "state": "done",
            "result_summary": "\n".join(summary_lines),
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
