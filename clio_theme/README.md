# clio_theme — Odoo 19 modul

Konfigurerbar navabar, sidebar och accentfarg per Odoo-databas.
Anvander CSS custom properties (CSS-variabler) som brygga mellan kompilerad SCSS och runtime-installningar.

## Funktion

SCSS kompileras vid install-tid och kan inte andras under drift.
Losningen: en `<style>`-tagg injiceras i `<head>` vid varje sidinladdning med CSS-variabler
fran databasens installningsrecord. Dessa variabler aasidosaatter SCSS-fallbacks via cascade-ordning
(style-blocket kommer efter link-taggen i dokumentet).

```
Databas-installning (clio.theme.config)
        |
        v
QWeb-template injectar <style> i <head>
        |
        v
CSS-variabel aaersidosaatter SCSS-fallback (samma selektor, senare i cascade)
```

## Installerade databaser och SCSS-fallbacks

| Databas      | Navbar            | Sidebar     |
|--------------|-------------------|-------------|
| aiab (prod)  | #2A3F6F (navy)    | #1a1a2e     |
| aiab19b (19) | #2A3F6F (navy)    | #1a1a2e     |
| ssf          | #1a6e6e (teal)    | #2d4a4a     |
| ssf19b       | #1a6e6e (teal)    | #2d4a4a     |
| *TEST*       | #e65c00 (orange)  | — (badge)   |
| *STAGING*    | #7b2d8b (lila)    | — (badge)   |

TEST/STAGING-badges aer haardkodade och paverkas INTE av installningar.

## CSS-variabler

| Variabel             | Element                        | SCSS-fallback        |
|----------------------|--------------------------------|----------------------|
| `--clio-nav-bg`      | Navbar bakgrund                | per databas          |
| `--clio-nav-border`  | Navbar understrecksaccent      | per databas          |
| `--clio-nav-text`    | Navbar text/brand              | #ffffff / per db     |
| `--clio-sidebar-bg`  | Sidebar vaenstermeny bakgrund  | ingen (transparent)  |
| `--clio-sidebar-text`| Sidebar text                   | ingen (arft)         |
| `--clio-primary`     | Akcentfarg (mappar ocksa till) |                      |
|                      | `--o-brand-primary`            |                      |
|                      | `--o-brand-action`             |                      |
|                      | `.btn-primary`                 |                      |
|                      | `.o_form_view label`           |                      |

## Konfiguration

Ga till **Clio -> Temainstaellningar** i Odoo-menyn (krav: systemadmin).

- Laemna ett faelt tomt for att anvanda SCSS-fallbackvaerdet.
- Det faar bara finnas **ett** installningsrecord per databas (singleton).
- Andringen slaar igenom direkt vid naesta sidinladdning — ingen omstart kravs.

## Behorighetsmodell

| Aatgard        | Krav               | Var det styrs                          |
|----------------|--------------------|----------------------------------------|
| Laesa CSS-vars | Alla anvandare     | QWeb-template anvander sudo()          |
| Se menyn       | base.group_system  | groups= pa menuitem                    |
| OEppna formulaer| base.group_system | groups_id pa ir.actions.act_window     |
| Redigera faelt | base.group_system  | groups= pa varje field i form view     |
| Skapa record   | base.group_system  | ir.model.access.csv + create()-override|
| Radera record  | base.group_system  | ir.model.access.csv                    |

Singleton-skydd: `create()` i modellen kastar `UserError` om ett record redan finns.

## Filstruktur

```
clio_theme/
|-  __init__.py
|-  __manifest__.py
|-  README.md                        (denna fil)
|-  models/
|   |-  __init__.py
|   |-  clio_theme_config.py         (clio.theme.config model)
|-  security/
|   |-  ir.model.access.csv          (lasa=alla, skriva=system)
|-  static/src/scss/
|   |-  theme.scss                   (CSS-variabler + SCSS-fallbacks)
|-  static/src/js/
|   |-  theme_detector.js            (data-db pa body vid JS-laddning)
|-  views/
    |-  templates.xml                (QWeb: data-db pa body + style-injektion)
    |-  theme_config_views.xml       (form, list, action, menuitem)
```

## Upgrade

```bash
docker exec odoo19-odoo-1 odoo -d <db> -u clio_theme --stop-after-init
```

## Beroenden

- `web` (Odoo-kerna)
- Inga externa Python-paket