# odoo_message_delete

Minimal modul som lägger till behörighetsgruppen **Radera meddelanden**.

## Problemet

Odoo 19 blockerar radering av `mail.message` på Python-nivå
(`_check_access` → `_get_forbidden_access` i `mail/models/mail_message.py`),
**utöver** ir.model.access och ir.rule. För unlink krävs skrivrätt på det
relaterade dokumentet — meddelanden utan `model`/`res_id` (t.ex. köade
utgående mail) nekas alltid, även för administratörer. Inga ACL- eller
ir.rule-poster hjälper.

## Lösningen

Modulen overridar `_get_forbidden_access` så att användare i gruppen
**Radera meddelanden** går förbi Python-spärren för just unlink.
Ordinarie ACL-kontroll (ir.model.access) gäller fortfarande.

## Användning

1. Installera modulen.
2. Ge gruppen *Radera meddelanden* till valda användare
   (Inställningar → Användare → fliken Behörigheter).
3. Användaren loggar ut och in igen.
4. Radera mail under Inställningar → Teknisk → E-post.

## Kompatibilitet

Odoo 19.0. (Odoo 18 har annan struktur på accesskontrollen i
`mail.message` — porta inte rakt av utan att kontrollera källkoden.)
