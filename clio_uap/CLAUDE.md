# clio_uap — Modul-kontext

Odoo 19 · db=`uap` · server: `clioadmin@100.107.127.104` · port 8079

## Uppdatera modulen
```bash
docker exec odoo19-odoo-1 odoo -c /etc/odoo/odoo.conf -u clio_uap -d uap --stop-after-init
docker restart odoo19-odoo-1
```

## Modeller

| Modell | Fil | Innehåll |
|---|---|---|
| `uap.encounter` | models/uap_encounter.py | Huvudobjekt — encounter med klassificering, ETH, observables |
| `uap.encounter.classification` | models/uap_encounter_classification.py | Multi-klassificering per encounter (Skywatcher, Transmorf, Hynek, ETH, custom) |
| `uap.report` | models/uap_report.py | Rårapport från källdatabas |
| `uap.source` | models/uap_source.py | Källkatalog (bok, artikel, webb, podd…) |
| `uap.database` | models/uap_database.py | Källdatabas (NUFORC, GEIPAN…) |
| `uap.series` | models/uap_series.py | Händelseserier med geo-bbox och konfidenspoäng |
| `uap.witness` | models/uap_witness.py | Vittnen |
| `uap.verification` | models/uap_verification.py | Per-fält verifieringslogg |
| `uap.anomaly` | models/uap_anomaly.py | **[Sprint 2]** Fenomen/mönster-index |
| `uap.anomaly.source` | models/uap_anomaly_source.py | **[Sprint 2]** Spårbarhet: anomali → rad i källa |

## uap.encounter.classification — system-värden

| system | Värden |
|---|---|
| `skywatcher` | I–X (Tetra, Tic Tac, Blob, Beam, Manta Ray, Bright Star, Jellyfish, Hornet, Egg, Teardrop) |
| `transmorf_entity` | Nordics, Tall Gray, Short Gray, Long Gray, Hybrid, Mantid / Insektoid, Reptilian, Energivarelse |
| `hynek` | CE1, CE2, CE3 |
| `eth` | 0–5 (Explained → Confirmed Non-Human) |
| `custom` | Fritext |

## Deprecated fält på uap.encounter
`skywatcher_class`, `skywatcher_confidence`, `skywatcher_notes` — kvar för bakåtkompatibilitet.
Ny data ska skrivas till `classification_ids` (system="skywatcher").
Migrering: se `~/19.0/clio-tools/clio-uap/migrate_classifications.py`

## uap.anomaly — anomaly_type-värden
`biological` · `atmospheric` · `contact` · `geographic` · `military` · `cosmological` · `transmorf` · `vehicle` · `other`

## Sprintlogg

### Sprint 1 (2026-09-26)
- Ny modell `uap.encounter.classification` — multi-klassificering per encounter
- `uap.encounter` fått `classification_ids` One2many + `classification_count`
- Ny flik "Klassificeringar" i encounter-form
- Versionsökning: 19.0.1.2.0 → 19.0.1.3.0
- Migrationsskript: `migrate_classifications.py` migrerar ~18 646 befintliga skywatcher-rader

### Sprint 2 (planerad)
- `uap.anomaly` + `uap.anomaly.source`
- Fenomenregister med spårbarhet till rad/tidsstämpel i källa

### Sprint 3 (2026-09-26)
- `uap.encounter` fått `anomaly_ids` Many2many + `anomaly_count`
- Smart button "Anomalier" i encounter-form
- Flik "Anomalier" i encounter-notebook
- Flik "Encounters" i anomali-form
- Versionsökning: 19.0.1.3.0 → 19.0.1.4.0
- Verifierat: alla 4 tabeller skapade, 18 646 skywatcher-rader migrerade

## Gotchas
- `_sql_constraints`-namn måste börja med `_` i Odoo 19
- XML `[@string='...']` är inte tillåtet — använd `[@name='fältnamn']`
- XML-kommentarer får inte innehålla `--` inuti texten
- Redigera lokalt → scp till servern (aldrig SSH-heredoc)
