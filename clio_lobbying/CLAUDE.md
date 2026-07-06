# Clio Lobbying — hur flödet är tänkt att fungera

## Syfte
Bevaka nyhetshändelser inom UFO/UAP och AI-domänerna, bygga en journalistdatabas
utifrån vem som skriver om ämnet, och generera riktade pitch-utkast när en ny
händelse dyker upp — så att Fredrik snabbt kan nå rätt journalist med rätt vinkel.

## Flödet steg för steg
1. **Bevakning** (clio-vigil, oberoende av Odoo) samlar löpande in artiklar per
   domän via RSS m.m. och lagrar dem i `vigil_items`.
2. **Byline-extraktion** (`journalist_extractor.py`, körs via `--extract-journalists`)
   plockar ut journalistnamn + publikation ur insamlade artiklar och
   skapar/uppdaterar poster i `clio.lobbying.journalist` (unik nyckel: namn+publikation).
   Generiska bylines (TT, Reuters, Staff, redaktionen m.fl.) filtreras bort.
3. **Profilbyggnad** (`--build-profiles`): Claude läser journalistens senaste
   artiklar och skriver en kort intresseprofil till `profile`-fältet — detta är
   underlaget pitch-matchningen bygger på.
4. Fredrik skapar en **händelse** (`clio.lobbying.event`) i Odoo: rubrik +
   beskrivning av nyheten som ska pitchas, samt vilken domän den hör till.
5. Knapparna **"Extrahera journalister"** och **"Generera pitchar"** på händelsen
   skriver en triggerfil som en systemd path-unit plockar upp och kör rätt
   pipeline-steg i bakgrunden (se Arkitektur nedan) — Fredrik behöver inte
   lämna Odoo eller vänta framför en terminal.
6. **Pitch-matchning** (`pitcher.py`, körs via `--pitch`): Claude matchar
   händelsen mot journalisternas profiler, skriver ett separat pitch-utkast
   per relevant journalist (`clio.lobbying.pitch`, state=`draft`), kopplat till
   händelsen. Ämnesrad extraheras automatiskt ur texten.
7. Fredrik **granskar** utkasten i Odoo (Pitch-kö), redigerar vid behov och
   **godkänner** (`approved`). Sändning sker fortfarande manuellt utanför denna
   knapp-automation — pitchen markeras `sent` när den faktiskt skickats.
8. Journalistens svar antecknas manuellt (`responded` + `response_notes`) för
   uppföljning och relationshistorik.

## Arkitektur — triggermekanismen
Odoo (knapptryck) → skriver JSON-triggerfil → systemd path-unit (bevakar filen,
körs på host, utanför Odoo-containern) → oneshot-service kör ett Python-skript
("runner") → runnern anropar `clio-vigil/main.py` med rätt flagga → resultatet
skrivs dels till lokal sqlite (`vigil.db`, tabellerna `journalists`/
`journalist_articles`/`pitch_runs`), dels synkas tillbaka till Odoo via
`odoo_writer.py` så att `clio.lobbying.journalist`/`clio.lobbying.pitch`
uppdateras. Odoo läser tillbaka status via ett beräknat fält (`trigger_status`)
som pollar en statusfil.

Samma trigger-mönster (fil → systemd → runner) används parallellt av den
generiska clio_vigil-pipelinen — de är fristående men delar mekanik.

## Modeller
- `clio.lobbying.event` — en nyhetshändelse, startpunkten för en pitch-omgång.
- `clio.lobbying.journalist` — en journalist + publikation, med intresseprofil
  och statistik (antal artiklar, senast sedd). Populeras automatiskt, kurateras
  manuellt (kontaktuppgifter, anteckningar).
- `clio.lobbying.pitch` — ett pitch-utkast riktat till en specifik journalist
  för en specifik händelse. Genereras av pipeline, godkänns/skickas manuellt.

## Domäner
`ufo` (UFO/UAP) och `ai` (AI-modeller) körs som två separata bevakningsspår
genom samma mekanik — journalister och händelser taggas med rätt domän så att
matchningen inte blandar ämnena.

## Status
Se projektminnet `project_clio_lobbying.md` och åtgärdsplanen för aktuellt
driftläge — denna fil beskriver det avsedda flödet, inte alltid vad som redan
är verifierat fungera i produktion.
