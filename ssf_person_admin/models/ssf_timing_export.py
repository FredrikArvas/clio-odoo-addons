import base64
import csv
import io

from odoo import fields, models


class SsfTimingExport(models.TransientModel):
    _name        = "ssf.timing.export"
    _description = "SSFTiming-export"

    competition_id = fields.Many2one(
        "ssf.competition", string="Tavling", required=True,
    )
    sector_id = fields.Many2one(
        "ssf.sector", string="Gren (filter)",
        help="Lamna tomt for alla grenar.",
    )
    attachment_id = fields.Many2one("ir.attachment", string="Fil", readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Klar")],
        default="draft", readonly=True,
    )

    def action_generate(self):
        self.ensure_one()
        comp = self.competition_id

        domain = [("competition_id", "=", comp.id)]
        if self.sector_id:
            domain.append(("sector_id", "=", self.sector_id.id))
        entries = self.env["ssf.entry"].search(domain)

        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow([
            "PersonID", "Fornamn", "Efternamn", "Fodelsear",
            "ChipNummer", "Organisation", "Gren",
        ])

        for entry in entries:
            person = entry.person_id
            if not person:
                continue
            chip_domain = [("partner_id", "=", person.id)]
            if self.sector_id:
                chip_domain.append(("sector_id", "=", self.sector_id.id))
            chip = self.env["ssf.person.chip"].search(chip_domain, limit=1)

            parts = (person.name or "").split(" ", 1)
            fornamn   = parts[0] if parts else ""
            efternamn = parts[1] if len(parts) > 1 else ""
            birth_year = person.birthdate_date.year if person.birthdate_date else ""

            writer.writerow([
                person.ref or "",
                fornamn,
                efternamn,
                birth_year,
                chip.chip_no if chip else "",
                person.parent_id.name if person.parent_id else "",
                entry.ccd_id.discipline_id.sector_id.name if entry.ccd_id and entry.ccd_id.discipline_id and entry.ccd_id.discipline_id.sector_id else "",
            ])

        csv_bytes = output.getvalue().encode("utf-8-sig")
        filename = "ssftiming_{}.csv".format((comp.name or str(comp.id)).replace(" ", "_"))

        attachment = self.env["ir.attachment"].create({
            "name": filename,
            "type": "binary",
            "datas": base64.b64encode(csv_bytes).decode(),
            "res_model": self._name,
            "res_id": self.id,
        })
        self.write({"attachment_id": attachment.id, "state": "done"})

        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/{}?download=true".format(attachment.id),
            "target": "self",
        }
