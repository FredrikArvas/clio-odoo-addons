# clio_media — CLAUDE.md

Delad artikelbank för Clio-agenter. Samlar alla nyhetsartiklar som analyseras av
`clio-agent-job` oavsett vilken modul (clio_recruit, clio_job, clio_vigil) som konsumerar dem.

---

## Syfte

`clio_media` är ett infrastrukturslager — den har ingen egen agent och skapar inga egna
matchningar. Artiklar skrivs hit av `clio-agent-job` via XML-RPC och länkas sedan som
`Many2one` från respektive matchmodell.

Modulen är designad för att växa: `media_type`-fältet är redo för poddar, videor och
andra medietyper i framtida iterationer.

---

## Datamodell

### `clio.media.article`

| Fält | Typ | Syfte |
|------|-----|-------|
| `article_id` | Char (index) | Extern nyckel från agenten (t.ex. hash av URL) |
| `url` | Char (index) | Artikelns URL |
| `title` | Char | Rubrik |
| `source` | Char | Källans namn, t.ex. "Di", "Breakit" |
| `media_type` | Selection | `article` (standard) — extensibel för framtida typer |
| `published` | Datetime | Publiceringstidpunkt |
| `first_seen` | Datetime | När agenten hämtade artikeln |
| `body_snippet` | Text | Utdrag (max ~1 000 tecken) |
| `match_score` | Integer | AI-poäng från analysen (−1 = ej analyserad) |
| `is_matched` | Boolean | Nådde matchtröskel för minst en profil |

---

## Koppling till agenten

`clio-agent-job` (i `~/18.0/clio-tools/clio-agent-job/`) skriver till `clio.media.article`
via funktionen `write_articles_to_odoo()` i `odoo_writer.py`.

Dedup-kontrollen (`load_known_article_ids()`) läser `article_id`-fältet i bulk för att
avgöra vilka artiklar som redan är sedda — en bulk-fråga per körning.

---

## Modulberoenden

```
clio_media          → base  (inga Clio-specifika beroenden)
clio_recruit        → clio_media  (article_id på clio.recruiter.match)
clio_job            → clio_media  (planerat — nästa iteration)
clio_vigil          → clio_media  (planerat — nästa iteration)
```

---

## Behörigheter

| Grupp | Artiklar |
|-------|----------|
| Role/User (1) | R |
| Role/Administrator (4) | R/W |

Artiklar skapas uteslutande av agenten via XML-RPC med admin-konto — aldrig manuellt.

---

## Menystruktur

```
Clio Media
└── Artiklar    (clio.media.article, list+form)
```

---

## Framtida mediatyper

Lägg till nya värden i `media_type`-Selection på `clio.media.article` och eventuellt
separata modeller (`clio.media.podcast` etc.) när agenten stöder fler typer.
`clio_media`-modulen äger namnrymden `clio.media.*`.

---

## Andra konsumenter: clio-research (media_research-spår)

Utöver `clio-agent-job` skriver även `clio-research` (`~/18.0/clio-tools/clio-research/odoo_media_writer.py`)
till `clio.media.article` — för medieanalysrapporter (t.ex. clio-research-004, UAP/UFO-bevakning).
Detta spår använder fler fält än grundmodellen ovan visar:

| Fält | Typ | Syfte |
|------|-----|-------|
| `country` / `language` | Char | Land/språk för artikeln |
| `author` | Char | Rå byline från källan (oftast tomt — GDELT/RSS saknar bylines) |
| `journalist_ids` | Many2many → res.partner | Kopplade journalist-kontakter (kräver A2-skrapning, ej byggd) |
| `tone` | Selection | neutral_faktabaserad / skeptisk / sensationalistisk / oklar |
| `article_type` | Selection | reaktiv / proaktiv |
| `thematic_frame` | Selection | nationell_sakerhet / vetenskap_astronomi / konspirationsteori / folklig_kultur / politisk_transparens / okategoriserad |
| `cited_actors` | Char (kommaseparerad) | militär, myndighet, forskare, vittne, politiker, skeptiker, ufolog_civilsamhälle |
| `temporal_marker_match` | Char | Datum för matchad tidsmarkör (±30 dagar) |
| `data_source` | Selection | gdelt / google_news_rss / vigil_ufo |
| `protocol_id` / `run_id` | Char (index) | Vilket clio-research-protokoll/körning artikeln kommer från |

**⚠️ Viktig gotcha (upptäckt 2026-07-07):** Modulen måste uppgraderas i **varje databas** där den
används efter schemaändringar — `state: installed` med gammal `latest_version` i `ir_module_module`
räcker inte, XML-RPC-`create()` misslyckas tyst (fångas av brett except) om en kolumn saknas i
databasschemat. Kör alltid:
```
docker exec odoo19-odoo-1 odoo -d <db> -u clio_media --stop-after-init
```
i **varje** databas som ska ta emot skrivningar (t.ex. både `aiab` och `uap`) — inte bara en.
