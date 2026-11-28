# clio_mail_admin — CLAUDE.md

Odoo-addon som exponerar clio-agent-mails admin-kommandon via Odoos gränssnitt.
Levererad och driftsatt 2026-04-21. NCC: #oadmin.

## Teknisk approach

- `clio_service.py` (clio-tools/clio-agent-mail/) — HTTP API port 7200, wrapprar `commands.dispatch()`
- `clio_mail_admin/` — TransientModel (wizard) + formulärvy med knappar
- Kommunikation: Odoo → HTTP → clio_service → commands.dispatch()
- Resultat visas i Odoo-popup (wizard reopen-pattern)
- Service-URL via systemparameter `clio.service.url` (satt till `http://172.19.0.1:7200` i aiab)

## Endpoints (clio_service.py)

| Path | Funktion |
|------|----------|
| `/health` | Hälsokontroll |
| `/mail/list` | list |
| `/mail/waiting` | waiting |
| `/mail/status` | status |
| `/mail/whitelist` | whitelist |
| `/mail/blacklist` | blacklist `{email}` |
| `/mail/interview/start` | `{to, subject, context}` |
| `/mail/interview/stop` | `{participant}` |
| `/mail/ncc/lista` | ncc_lista |
| `/mail/ncc/ny` | `{kodord, namn, sfar, ...}` |
| `/mail/update` | `{kodord, content}` |

## Gotchas

- `localhost` i systemparameter fungerar inte inifrån containern — använd gateway-IP `172.19.0.1`
- `clio_service` är en systemd-tjänst på EliteDesk (port 7200) — verifiera med `systemctl status clio_service`
