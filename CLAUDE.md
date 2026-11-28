# clio-odoo-addons — CLAUDE.md

## Repo

Odoo 19-addons för Clio-plattformen (Arvas International AB).
Server: clioadmin@100.107.127.104 → `~/clio-odoo-addons/`
Instans: https://app.arvas.international (db=aiab, container=odoo19-odoo-1)

Generell Odoo 19-kodstandard: se `ODOO19_STD.md` i detta repo.

---

## Deploy-flöde

Redigera lokalt → scp till servern → backup på servern → uppdatera modul → starta om container.

```powershell
# 1. Kopiera ändrade filer till servern (aldrig SSH-heredoc)
scp -r clio-modulnamn/ clioadmin@100.107.127.104:~/clio-odoo-addons/

# 2. På servern: backup + moduluppdatering
ssh clioadmin@100.107.127.104
cp -r ~/clio-odoo-addons/clio-modulnamn ~/clio-odoo-addons/clio-modulnamn.bak-$(date +%Y%m%d%H%M)
docker exec odoo19-odoo-1 odoo --database aiab --update clio_modulnamn --stop-after-init --no-http

# 3. Starta om container
docker restart odoo19-odoo-1
```

SSH-nycklar: `~/.ssh/github_clio` → FredrikArvas, `~/.ssh/examensbyran_deploy` → Examensbyran.

---

## Vykrav — alla Odoo-moduler

Varje modul som exponerar data ska ha **fyra vyer** i XML:

```xml
<field name="view_mode">list,kanban,pivot,graph</field>
```

- **list** — standardvy, med `decoration-success/warning/danger` för statusfärgning
- **kanban** — kort-vy, minst status-fält och namn
- **pivot** — aggregering, minst ett measure-fält
- **graph** — diagram, minst ett measure + group_by

Undantag tillåts bara för rent transaktionella modeller utan aggregeringsvärde (t.ex. logg-tabeller).

**Vanligt fel — `colspan` på textfält i formulär:**
Långa textfält (`widget="text"`) tar bara halv formulärbredd om `colspan="2"` saknas.
Lägg alltid till `colspan="2"` på `<field widget="text" ...>` inuti `<group>`:

```xml
<field name="target_characteristics"
       widget="text" placeholder="…" nolabel="1" colspan="2"/>
```

---

## Encoding — åäö och BOM

**BOM i Python-filer** är den vanligaste orsaken till att Odoo vägrar ladda en modul.

Regler:
- Skriv alltid filer med Claude Code `Write`-verktyget — aldrig PowerShell `Out-File` eller `Set-Content` (de lägger BOM som standard)
- XML-filer ska alltid börja med `<?xml version="1.0" encoding="utf-8"?>`
- Python-filer behöver **inte** `# -*- coding: utf-8 -*-` i Python 3, men det skadar inte

Diagnos vid mystisk laddningsfel:
```bash
# Kolla BOM på servern
file ~/clio-odoo-addons/clio_modul/__init__.py
# → "UTF-8 Unicode (with BOM) text" = problem
# → "Python script, UTF-8 Unicode text" = ok

# Ta bort BOM
sed -i 's/^\xef\xbb\xbf//' ~/clio-odoo-addons/clio_modul/__init__.py
```

Loggfil vid moduluppdatering: `docker logs odoo19-odoo-1 2>&1 | tail -50`
