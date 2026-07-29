# ADD — Clio Bridge för gsf_jubileum

**Status:** Beslutad för bygge | **Datum:** 2026-07-29 | **Författare:** Clio (granskningssession) + Fredrik Arvas
**Byggs i:** separat session på EliteDeskGPU (clioadmin@100.107.127.104)
**Relaterat:** NCC #gsford, repo `FredrikArvas/clio-odoo-addons` branch `19.0`, katalog `gsf_jubileum/`

---

## 1. Bakgrund

`gsf_jubileum` samlar in fastighetsberättelser till Guldboda SF:s 80-årsjubileum via en
token-baserad publik chattsida (`/jubileum/<token>`). Idag anropar Odoo-controllern
(`controllers/portal.py`) Anthropic-API:t direkt med `anthropic`-SDK:n. Granskning
2026-07-29 identifierade tre problem som denna bridge löser:

1. **Ingen rate-limiting eller längdtak** — publika endpoints kan missbrukas (API-kostnad, DB-svullnad).
2. **Hela historiken skickas om vid varje anrop** — växande payload, race condition vid samtidiga anrop (läs-modifiera-skriv på `coaching_history`).
3. **Naiv svarsparning vid inlämning** — user-meddelanden paras 1:1 med frågorna i ordning; följdfrågor förskjuter mappningen så svar hamnar på fel fråga i `svar_ids`.

Önskemål från Fredrik: använd Claude-subscriptionen i stället för betalda API-anrop där det går.

## 2. Mål och icke-mål

**Mål**
- All LLM-trafik går via en lokal bridge-tjänst — Odoo pratar aldrig direkt med Anthropic.
- Äkta sessionshantering per fastighet (resume i stället för att skicka om historiken).
- Subscription-autentisering som primärt backend, API-nyckel som konfigurerbart alternativ.
- LLM-baserad svarsextraktion vid inlämning (ersätter 1:1-parningen).
- Tak: maxlängd per meddelande, max antal växlingar per fastighet, enkel rate-limit per IP/token.

**Icke-mål**
- Ingen ändring av besökar-UX (chattsidan, samtyckespanelen, mailflödet behålls).
- Ingen streaming i v1 — request/response räcker (svaren är korta, max_tokens 600).
- Ingen multi-tenant — bridgen är dedikerad för gsf-databasen.

## 3. Arkitektur

```
Besökare ──► Odoo (gsf, port 8079, container odoo19-odoo-1)
                 │  controllers/portal.py
                 │  HTTP POST localhost:8090 (delad hemlighet i header)
                 ▼
             clio-bridge-gsf (FastAPI, systemd, EliteDeskGPU-host)
                 │  Claude Agent SDK (python), headless
                 │  auth: subscription-OAuth-token (claude setup-token)
                 │  fallback: ANTHROPIC_API_KEY
                 ▼
             Anthropic (Claude)
```

- **Placering:** `~/19.0/clio-tools/clio-bridge-gsf/` på EliteDeskGPU (host, ej i container —
  containern når hosten via `host.docker.internal` eller host-IP; verifiera vilket som
  fungerar i odoo19-compose-nätverket, annars bind bridgen på docker-bryggans IP).
- **Process:** systemd-tjänst `clio-bridge-gsf.service`, user clioadmin, restart=always.
- **Odoo behåller `coaching_history`** som journal/backup och för redaktörsvyn — bridgen är
  källan för samtalskontexten, Odoo är källan för det sparade resultatet.

## 4. API-kontrakt (bridge)

Alla anrop kräver header `X-Bridge-Secret: <delad hemlighet>`. Bind endast på localhost/docker-brygga.

### POST /chat
```json
Request:  {"fastighet_token": "<uuid>", "namn": "Guldboda 1:23", "message": "..."}
Response: {"reply": "...", "session_id": "...", "turns": 7}
Fel:      {"error": "for_langt_meddelande" | "for_manga_turer" | "rate_limit" | "backend_fel"}
```
- Bridgen håller mappning `fastighet_token → session_id` (SQLite-fil i tjänstekatalogen).
- Finns ingen session: skapa ny med systemprompt (flyttas från portal.py till bridgen,
  frågelistan läses från en kopia av `fragor.py` eller skickas med i första anropet — **beslut: skicka
  med `fragor` i request** så modulen förblir enda källan).
- Finns session: resume via Agent SDK — endast nya meddelandet skickas.
- Tak (konfigurerbara i `.env`): `MAX_MESSAGE_CHARS=4000`, `MAX_TURNS=60`,
  `RATE_LIMIT=10 anrop/min per token`.

### POST /extract
Anropas av Odoo vid submit (ersätter 1:1-parningen i `jubileum_submit`).
```json
Request:  {"fastighet_token": "<uuid>", "history": [{"role": "...", "content": "..."}],
           "fragor": [[1, "Öppning", "Vilken tomt..."], ...]}
Response: {"svar": {"1": "...", "2": "", ...}}
```
- Ett LLM-anrop: "mappa samtalet till frågorna, returnera JSON, tom sträng där svar saknas".
- Vid fel eller ogiltig JSON: returnera `{"svar": null}` — Odoo lämnar då `svar_ids` tomt
  och redaktören arbetar från rå-JSON:en. Inlämningen får aldrig blockeras av extraktionsfel.

### GET /health
`{"status": "ok", "backend": "subscription" | "api", "sessions": <antal>}`

## 5. Backend-val och autentisering

| | Primärt: subscription | Fallback: API |
|---|---|---|
| Auth | OAuth-token via `claude setup-token` (Max-prenumeration) | `ANTHROPIC_API_KEY` |
| Kostnad | 0 kr extra | ~några dollar totalt för hela insamlingen |
| Risk | ToS-gråzon (personligt bruk), delade rate limits — kan strypa vid samtidiga besökare | Ingen |
| Modell | Den SDK:n ger (Sonnet-klass) | `claude-haiku-4-5-20251001` räcker för intervjun; extraktion: samma |

- Val styrs av `.env`: `BRIDGE_BACKEND=subscription|api`. Byte kräver bara omstart av tjänsten.
- **Rekommendation i drift:** kör subscription under test/pilot; slår rate limits till vid
  massutskick (t.ex. efter stämmokallelse) → växla till `api`.
- Tokens/nycklar i `.env` med mode 600 — aldrig i git, aldrig i klartext i loggar eller svar.

## 6. Ändringar i gsf_jubileum (Odoo-sidan)

1. `controllers/portal.py`:
   - `jubileum_chat`: ersätt anthropic-blocket med `requests.post(BRIDGE_URL + "/chat", ...)`.
     Historik-append till `coaching_history` behålls (journal). Befintliga statusspärrar behålls.
   - `jubileum_submit`: ersätt parningsloopen med anrop till `/extract`; skapa `svar_ids`
     från svaret, hoppa över om `svar: null`.
2. Nya `ir.config_parameter`: `gsf.bridge.url` (default `http://host.docker.internal:8090`),
   `gsf.bridge.secret`. Befintliga `gsf.anthropic.api_key`-parametrar fasas ut ur controllern
   (behålls i db tills bridgen är verifierad).
3. `__manifest__.py`: `anthropic` behövs inte längre i containern (requests finns i Odoo-basen).
4. Felhantering: bridge onåbar → samma användarmeddelande som idag
   ("AI-tjänsten är tillfälligt otillgänglig...").

## 7. Sessionshantering och samtidighet

- Bridgen serialiserar anrop per `fastighet_token` (asyncio-lås per token) — löser racet.
- Sessioner äldre än 30 dagar utan aktivitet rensas (cron i tjänsten); vid resume-miss
  återskapas sessionen från `history` som Odoo skickar med (fältet `history` är därför
  med i `/chat`-requesten som fallback, används endast vid session-miss).
- SQLite-schema: `sessions(fastighet_token TEXT PK, session_id TEXT, turns INT, updated_at TEXT)`.

## 8. Deploy och verifiering

1. Bygg i `~/19.0/clio-tools/clio-bridge-gsf/` (venv, requirements: fastapi, uvicorn,
   claude-agent-sdk, httpx). Filer skrivs lokalt + scp (aldrig heredoc).
2. `claude setup-token` körs manuellt av Fredrik på servern (interaktivt OAuth-steg).
3. systemd-enhet + `.env`; verifiera `/health` innan Odoo-ändringarna deployas.
4. Odoo-ändringar: commit på `19.0`, `-u gsf_jubileum` i **testdatabas först** om sådan finns,
   annars prod med checkpoint (en produktionshandling i taget, verifiera efter varje).
5. Acceptanskriterier:
   - [ ] Chatt fungerar end-to-end på `/jubileum/<token>` (ny + återupptagen session)
   - [ ] Två parallella anrop på samma token tappar inga meddelanden
   - [ ] Meddelande > 4000 tecken avvisas snyggt i UI
   - [ ] Submit fyller `svar_ids` korrekt även när Clio ställt följdfrågor
   - [ ] Bridge nere → användarvänligt fel, inget 500
   - [ ] Inga hemligheter i loggar; `.env` mode 600
   - [ ] `docker logs odoo19-odoo-1` fritt från gsf-ERROR efter deploy

## 9. Öppna frågor till byggsessionen

- Verifiera hur containern når hosten (`host.docker.internal` finns inte alltid i
  Linux-docker utan `extra_hosts` — kan kräva rad i compose-filen).
- Agent SDK:s resume-mekanik mot subscription-auth: verifiera tidigt (spike) innan
  resten byggs — om resume inte bär, degradera till stateless-läge (skicka historik)
  men behåll bridgens tak och serialisering, som ger värde ändå.
- Modellval för `/extract` vid `api`-backend (Haiku 4.5 föreslås — strukturerad extraktion).
