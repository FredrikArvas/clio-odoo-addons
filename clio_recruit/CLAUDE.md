# clio_recruit — CLAUDE.md

Odoo-modulen för **Clio Recruit**: passiv kandidatsourcing driven av marknadssignaler.
Modulen är ett gränssnitt mot den fristående agenten `clio-recruiter` som körs på EliteDeskGPU.

---

## Syfte

Clio Recruit hjälper rekryterare att identifiera kandidater *innan* de aktivt söker jobb,
genom att bevaka nyhetsflöden efter signaler som varsel, plattformsbyten, outsourcing
och organisationsförändringar.

Modulen lagrar **rekryterarprofiler** (vad/vem söks) och **matchhistorik** (vilka
signaler har genererats och skickats). Själva AI-analysen och mailutskicken sköts av
`clio-recruiter` utanför Odoo.

---

## Datamodell

### `clio.recruiter.profile`
En profil per rekryteringsuppdrag. Definierar vad clio-recruiter ska leta efter.

| Fält | Typ | Syfte |
|------|-----|-------|
| `name` | Char (required) | Internt uppdragsnamn, t.ex. `"Capgemini — Integration Architect"` |
| `partner_id` | Many2one → `res.partner` | Mottagarkontakt för signalrapporter |
| `email` | Char (computed, store=True) | Beräknat från `partner_id.email` — läses av agenten via XML-RPC |
| `language` | Selection (sv/en) | Rapportspråk |
| `target_role` | Char | Målroll, t.ex. `"Integration Solution Architect"` |
| `target_seniority` | Char | Senioritetsnivå, t.ex. `"Senior (5+ år)"` |
| `target_characteristics` | Text | Egenskaper att leta efter — en per rad |
| `target_avoid` | Text | Profiler att exkludera — en per rad |
| `target_industries` | Text | Branscher att bevaka — en per rad |
| `trigger_signals_high` | Text | Marknadshändelser med hög kandidattillgång — en per rad |
| `trigger_signals_medium` | Text | Sekundära signaler att bevaka — en per rad |
| `client_hint` | Char | Klientbeskrivning i rapporter (klar text eller alias) |
| `confidential_client` | Boolean | Dölj klientnamn i utskick (default: True) |
| `active` | Boolean | Arkivera utan att radera |
| `match_ids` | One2many → `clio.recruiter.match` | Matchhistorik |

### `clio.recruiter.match`
En post per artikel/signal som nått matchtröskel och generat en rapport.
Skapas av `clio-recruiter`, **inte** manuellt i Odoo.

| Fält | Typ | Syfte |
|------|-----|-------|
| `profile_id` | Many2one (required) | Vilken rekryterarprofil matchen tillhör |
| `article_url` | Char | Källartikel |
| `article_title` | Char | Artikelrubrik |
| `target_company` | Char | Bolaget signalen gäller |
| `candidate_profile` | Char | Typ av kandidat som berörs |
| `signal_type` | Char | t.ex. `outsourcing`, `varsel`, `s4hana_migration`, `cio_byte` |
| `match_score` | Integer | 0–100 från AI-analysen |
| `estimated_timeline` | Char | Uppskattad tid tills kandidater är tillgängliga |
| `contact_hint` | Char | Hur man bäst når kandidaterna |
| `recommended_action` | Char | t.ex. `kontakta_nu`, `bevaka_3_mån`, `skip` |
| `sent_at` | Datetime | När rapporten skickades |

---

## Koppling till clio-recruiter

Agenten `clio-recruiter` körs som ett fristående Python-projekt på EliteDeskGPU:
- Sökväg: `~/git/clio-recruiter/`  
- Läser profiler från Odoo via XML-RPC
- Analyserar nyhetsflöden med Claude och poängsätter mot profilernas signalnyckelord
- Skickar rapport via clio-agent-mail till `email` på profilen (beräknat från `partner_id.email`)
- Skriver tillbaka matchposter till `clio.recruiter.match` via XML-RPC

Modulen är **read-mostly** för användaren — profilerna justeras i Odoo,
matchhistoriken skrivs av agenten.

---

## Behörigheter

| Grupp | Profiler | Matchhistorik |
|-------|----------|---------------|
| Role/Administrator (4) | R/W | R/W |
| Role/User (1) | R | R |

Inga kandidat-specifika postfilter (till skillnad från `clio_job` som har
`ir.rule` för Clio Kandidat-gruppen).

---

## Menystruktur

```
Clio Recruit
├── Rekryterarprofiler   (clio.recruiter.profile, list+form)
└── Matchhistorik        (clio.recruiter.match, list+form)
```

---

## Vanliga operationer

**Ny rekryterarprofil** — skapa direkt i Odoo eller via XML-RPC:
```python
m.execute_kw(db, uid, pwd, 'clio.recruiter.profile', 'create', [{
    'name':               'Kund — Roll',
    'email':              'rekryterare@example.com',
    'target_role':        'Integration Solution Architect',
    'target_seniority':   'Senior (5+ år)',
    'trigger_signals_high': 'Varsel på integrationstunga bolag\nBizTalk-migrationer',
    'confidential_client': False,
    'client_hint':        'Capgemini Sverige',
}])
```

**Justera signalnyckelord** — redigera `trigger_signals_high`/`trigger_signals_medium`
direkt i Odoo-formuläret. Agenten läser dem vid nästa körning.

**Arkivera avslutad rekrytering** — sätt `active = False` på profilen.
Matchhistoriken bevaras.

---

## res.partner-integration

En "Clio Recruit"-flik visas på kontaktkortet för partners som är mottagare av en profil.
Fliken listar alla profiler kopplade till partnern med roll och antal matchningar.

Fältet `email` på profilen är computed och lagras (`store=True`) — agenten kan fortsätta
läsa det via XML-RPC utan ändringar.
