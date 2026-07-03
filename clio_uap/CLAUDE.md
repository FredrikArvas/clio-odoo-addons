# clio_uap — CLAUDE.md

## Vad är det här?
Odoo 19-addon för UAP-forskning (Unidentified Aerial Phenomena). Samlar, klassificerar
och analyserar UAP-observationer globalt med källkritisk metodik.

## Sökvägar
- Addon: `~/clio-odoo-addons/clio_uap/`
- Migreringsskript: `~/19.0/clio-tools/clio-uap/`
- Odoo 19: `http://localhost:8079`, db=`uap`
- Odoo 18 (källa): `http://localhost:8069`, db=`uapdb`

## Modeller

| Modell | Beskrivning | Poster (efter migrering) |
|---|---|---|
| `uap.encounter` | Huvudmodell — UAP-observationer | ~2 763 |
| `uap.source` | Källor (böcker, arkiv, media) | ~58 |
| `uap.witness` | Vittnen | ~25 |
| `uap.verification` | Ändringslogg per encounter | ~13 |
| `uap.series` | Händelseserier (wave, swarm...) | 0 (ny) |
| `uap.database` | Organisationsdatabaser | 0 (ny) |
| `uap.report` | Råimport från externa källor | 0 (ny) |
| `uap.encounter.witness` | Through-modell encounter↔vittne | 0 (ny) |

## Klassificeringssystem (3-dimensionellt)
- **Encounter Class** (1-4): Sighting → Close Encounter → Physical Evidence → Contact
- **Discourse Level** (1-5): Fringe → Limited → Active Debate → Official → Confirmed
- **Official Response** (A-E): No Response → Denial → Acknowledgement → Investigation → Confirmation

## Addon-version
`19.0.1.1.0` — portad från Odoo 18, tilläggsmodeller portade 2026-06-24.

## Viktiga beslut
- `uap.series`/`uap.database` finns i 19-addonen men saknar data från 18 (modellerna
  existerade ej i uapdb).
- `res.country` IDs är identiska mellan 18 och 19 — ingen mapping behövs.
- Migrering sker via XML-RPC (inte DB-dump) för att hålla Odoo-relationer intakta.
- clio-bot (`clio-bot@arvas.international`) är service-account för skript.

## Köra migrering
```bash
python3 ~/19.0/clio-tools/clio-uap/migrate_to_19.py
```

## Vanliga kommandon
```bash
# Uppdatera addon efter kodändring
docker exec odoo19-odoo-1 odoo --database uap --update clio_uap --stop-after-init --no-http

# Räkna poster via Python
python3 -c "
import xmlrpc.client
url='http://localhost:8079'; db='uap'
# Läs lösenord från .env
"
```

## Beroenden
- `base`, `contacts` (Odoo core)
- Ingen OCA-modul krävs

## Nästa steg (Sprint E)
1. Landfördelning — vilka länder har flest fall?
2. Disclosure-analys — klassiska fall i flera Wikipedia-utgåvor
3. Rapport/blogg för Karl Hemborg + Thomas ET Persson
4. Nästa datakälla: NUFORC CSV (150 000+ US-rapporter)
