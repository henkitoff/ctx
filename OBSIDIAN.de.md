[🇬🇧 English](OBSIDIAN.md) · 🇩🇪 Deutsch

# Obsidian-Setup — Menschen und Agenten, ein Vault

Dieses `.ctx`-Repository ist so konzipiert, dass **dieselben Dateien zwei Zielgruppen gleichwertig dienen**:

- **Menschen** navigieren über Obsidians Graph-Ansicht, Backlinks, Canvas, Dataview-Tabellen
- **Agenten** navigieren über `INDEX.md`, `CROSS_INDEX.json`, `LATEST.yaml` und destillierte Tier-Dateien

Keine Duplizierung. Kein „Docs für Menschen, separater Kontext für Agenten." Eine einzige Quelle der Wahrheit.

---

## So funktioniert es: der Dual-Audience-Vertrag

| Feature | Menschliche Erfahrung | Agenten-Erfahrung |
|---------|----------------------|-------------------|
| YAML-Frontmatter | Obsidian-Properties-Panel | Maschinenlesbare Metadaten |
| `INDEX.md` | Einstiegsnotiz / Startseite | Pflicht-Erstlektüre |
| `CROSS_INDEX.json` | — (Menschen nutzen Canvas) | Abhängigkeitsgraph, kein Parsen nötig |
| `modules/*.ctx.md` | Reiches Markdown mit Properties | Moduldoku mit tier-getaggten Abschnitten |
| Tier-Tags `<!-- all-tiers -->` | Im gerenderten View unsichtbar | Steuert, was destillierte Tiers enthalten |
| `.distilled/haiku/` | — (Menschen lesen Master-Dateien) | Token-effizienter Kontext für schnelle Modelle |
| `knowledge/LATEST.yaml` | Lebende Projektstatus-Notiz | Session-Übergabe, wird zu Beginn jeder Session gelesen |
| Canvas `.canvas` | Visuelle Architekturübersicht | — (Agenten nutzen CROSS_INDEX.json) |
| Dataview-Abfragen | Automatisch generierte Modultabellen | — |

---

## 1. Vault-Einrichtung

### Option A — `.ctx/` innerhalb eines bestehenden Projekt-Vaults (empfohlen)

Dein Projekt hat bereits einen Obsidian-Vault im Repository-Root. Füge `.ctx/` als Unterordner hinzu:

```
my-project/          ← Obsidian-Vault-Root
├── .obsidian/
├── .ctx/            ← Dieses Repo, als Unterordner geklont
│   ├── INDEX.md
│   ├── modules/
│   ├── architecture/
│   ├── knowledge/
│   └── scripts/
├── src/
├── docs/
└── README.md
```

In Obsidian → Einstellungen → Dateien & Links: **Standard-Speicherort für neue Notizen** auf deinen `docs/`-Ordner setzen, nicht `.ctx/`.

### Option B — `.ctx/` IST der Vault

Dieses Repo direkt klonen und in Obsidian als Vault öffnen. Geeignet für reine Wissensdatenbanken, Dokumentationsprojekte oder wenn `.ctx/` der primäre Arbeitsbereich sein soll.

```
ctx/                 ← Obsidian-Vault-Root (dieses Repo)
├── .obsidian/       ← Von Obsidian erstellt
├── INDEX.md
├── modules/
├── architecture/
├── knowledge/
└── scripts/
```

---

## 2. Plugins installieren

Obsidian → Einstellungen → Community-Plugins → Durchsuchen

| Plugin | Zweck | Erforderlich? |
|--------|-------|---------------|
| **Dataview** | Automatisch generierte Modultabellen aus Frontmatter | Empfohlen |
| **Templater** | Einheitliche Erstellung neuer Module | Empfohlen |
| **Kanban** | `open_items` aus Knowledge-Distillaten verfolgen | Optional |
| **Git** | Knowledge-Distillate direkt aus Obsidian committen | Optional |

---

## 3. Frontmatter als Obsidian-Properties

Jede `.ctx.md`-Datei hat YAML-Frontmatter, das Obsidian als **Properties** rendert.
`tags` und `aliases` hinzufügen, um das Beste aus Graph-Ansicht und Suche herauszuholen:

```yaml
---
module: modules/auth
type: codebase
depends_on: [database, cache]
depended_by: [api, billing]
provides: [AuthService, TokenValidator, SessionManager]
invariants:
  - "Tokens are never stored in plaintext"
keywords: [auth, jwt, session, oauth]

# Obsidian-spezifische Ergänzungen (kein Effekt auf Agenten):
tags: [ctx/module, ctx/codebase]
aliases: [AuthService, auth-module]
---
```

**Tag-Konvention:**
- `ctx/module` — alle Moduldokumente
- `ctx/architecture` — alle Architekturdokumente
- `ctx/knowledge` — alle Knowledge-Distillate
- `ctx/example` — Beispiel-/Template-Dateien (aus Produktionsabfragen herausfiltern)

---

## 4. Graph-Ansicht — den Abhängigkeitsgraphen visuell sehen

Einstellungen → Graph-Ansicht → Filter:

**Nur Moduldokumente anzeigen:**
```
tag:#ctx/module OR tag:#ctx/architecture
```

**Farbgruppen (Einstellungen → Graph-Ansicht → Gruppen):**
- `tag:#ctx/module` → Blau
- `tag:#ctx/architecture` → Orange
- `tag:#ctx/knowledge` → Grün

**Profi-Tipp:** `[[wikilinks]]` in `.ctx.md`-Dateien einfügen, um Kanten im Graph zu erzeugen:

```markdown
## Querverweise  <!-- all-tiers -->

- Hängt ab von: [[modules/database.ctx|database]]
- Hängt ab von: [[modules/cache.ctx|cache]]
- Genutzt von: [[modules/api.ctx|api]]
```

---

## 5. Dataview — Live-Modultabellen

Dataview-Plugin installieren, dann diese Abfragen in eine beliebige Notiz einfügen:

### Alle Module mit Abhängigkeiten

````markdown
```dataview
TABLE
  provides AS "Exports",
  depends_on AS "Hängt ab von",
  depended_by AS "Genutzt von"
FROM "modules"
WHERE type = "codebase" AND !contains(tags, "ctx/example")
SORT module ASC
```
````

### Module nach Stichwort

````markdown
```dataview
LIST
FROM "modules"
WHERE contains(keywords, "auth") OR contains(keywords, "security")
```
````

### Neueste Knowledge-Distillate

````markdown
```dataview
TABLE topic AS "Thema", milestone AS "Meilenstein"
FROM "knowledge"
WHERE date != null
SORT date DESC
LIMIT 5
```
````

---

## 6. Templater — neue Module einheitlich erstellen

Einstellungen → Templater → **Template-Ordner-Pfad**: `obsidian/templates`

Einstellungen → Templater → **Ordner-Templates**:
- `modules/` → `obsidian/templates/new-module.md`
- `architecture/` → `obsidian/templates/new-architecture.md`
- `knowledge/` → `obsidian/templates/new-knowledge.md`

**Nach dem Ausfüllen des Templates** das Build-Skript ausführen:
```bash
python scripts/build_distilled.py
```

---

## 7. Canvas — Architektur als lebendes Diagramm

`architecture.canvas` im Vault-Root erstellen und aus `CROSS_INDEX.json` aufbauen:
1. Ein Knoten pro Modul → mit `modules/X.ctx.md` verknüpfen
2. Ein Knoten pro Service (Redis, Postgres, S3 …)
3. Pfeile für `depends_on`-Beziehungen einzeichnen
4. Farbcodierung: Module blau, Services grau, Architekturdokumente orange

**Synchronisationsregel:** Immer wenn du ein Modul zu `CROSS_INDEX.json` hinzufügst, füge einen Knoten zum Canvas hinzu.

---

## 8. Knowledge-Distillate als lebende Notizen

`knowledge/LATEST.yaml` ist gleichzeitig YAML-Datei für Agenten und Obsidian-Notiz.

**LATEST.yaml als Vault-Startseite anpinnen:**
Einstellungen → Core-Plugins → **Mit Stern markiert** → `knowledge/LATEST.yaml` markieren

---

## 9. Tier-Tags — für dich unsichtbar, für Agenten unverzichtbar

Tier-Tags (`<!-- all-tiers -->`, `<!-- sonnet+ -->`, `<!-- opus-only -->`) sind HTML-Kommentare — in Obsidian vollständig unsichtbar im Lese- und Live-Preview-Modus.

- **Menschen** lesen die vollständige Master-Datei — alle Abschnitte sichtbar
- **Agenten** lesen die tier-passende destillierte Datei — nur relevante Abschnitte

```markdown
## Neuer Abschnitt  <!-- sonnet+ -->

Dieser Abschnitt erscheint nur in .distilled/sonnet/ und .distilled/opus/.
```

---

## 10. Agenten-Dispatch-Regel in INDEX.md

```markdown
## Agenten-Dispatch-Regel

| Modellgröße | Diese Datei laden |
|-------------|-------------------|
| Haiku / schnelle Worker | .distilled/haiku/{module}.ctx.md |
| Sonnet / Manager-Agenten | .distilled/sonnet/{module}.ctx.md |
| Opus / Architektur-Aufgaben | modules/{module}.ctx.md |
```

---

## 11. Täglicher Workflow

### Als Mensch

| Wann | Was tun |
|------|---------|
| Tagesbeginn | `knowledge/LATEST.yaml` öffnen → `next_session_hints` prüfen |
| Neues Modul | Cmd+N → Template → ausfüllen → `build_distilled.py` |
| Session-Ende | `python scripts/new_knowledge.py "thema"` → ausfüllen |
| Architekturänderung | Canvas + `CROSS_INDEX.json` aktualisieren |

### Als / mit einem Agenten

| Wann | Was der Agent liest |
|------|---------------------|
| Session-Start | `INDEX.md` → `knowledge/LATEST.yaml` → `next_session_hints` |
| Modulaufgabe | `.distilled/{tier}/{module}.ctx.md` |
| Architektur-Aufgabe | `architecture/{PATTERN}.ctx.md` + `CROSS_INDEX.json` |

---

## 12. Schnellstart-Checkliste

**Einmalige Einrichtung (15 Min.):**
- [ ] Repo als Obsidian-Vault öffnen (oder `.ctx/` zum bestehenden Vault hinzufügen)
- [ ] Installieren: Dataview + Templater
- [ ] Templater-Ordner-Templates setzen
- [ ] `tags: [ctx/module]` zum Frontmatter bestehender Moduldateien hinzufügen
- [ ] Graph-View-Farbgruppen konfigurieren
- [ ] `knowledge/LATEST.yaml` als Vault-Startseite anpinnen

**Projektbezogene Einrichtung (30 Min.):**
- [ ] Eine `modules/X.ctx.md` pro Fachbereich erstellen
- [ ] `CROSS_INDEX.json` mit realen Abhängigkeiten befüllen
- [ ] `python scripts/build_distilled.py` ausführen
- [ ] `architecture.canvas` erstellen
- [ ] Dispatch-Regel zu `CLAUDE.md` / `AGENTS.md` hinzufügen

---

## 13. Was NICHT in `.ctx/` gehört

| Nicht in `.ctx/` | Stattdessen hier |
|-----------------|------------------|
| Meeting-Notizen, Tagesnotizen | `docs/journal/` |
| Entwurfsspezifikationen | `docs/specs/` |
| Persönliche Code-Anmerkungen | Code-Kommentare in der Quelle |
| Screenshots, Diagramme | `docs/assets/` |

**Der Test:** Würde ein Agent dadurch verwirrt? Falls ja, gehört es nicht in `.ctx/`.

---

## Navigation

[[INDEX]] · [[GUIDE.de]] · [[README]] · [[CLAUDE]] · [[AGENTS]] · [[modules/example.ctx|Beispiel-Modul]] · [[examples/openclaw/INDEX|OpenClaw-Beispiel]]
