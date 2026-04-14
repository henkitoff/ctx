[🇬🇧 English](GUIDE.md) · 🇩🇪 Deutsch

# .ctx — Vollständiger Setup- und Nutzungsguide

---

## Warum .ctx + Distillation? Der echte Vorteil

Ohne `.ctx` macht jeder Agent bei null an — er liest entweder zu wenig (halluziniert)
oder zu viel (kostet Unsummen). Mit `.ctx` hat jedes Modell genau die Information,
die es für seine Aufgabe braucht. Nicht mehr. Nicht weniger.

### Das Kernproblem ohne .ctx

Ein Agent der auf einem 300-Datei-Projekt arbeitet:
- Liest 10 zufällige Dateien und halluziniert den Rest
- Oder du schreibst den Kontext von Hand in jeden Prompt — jedes Mal
- Bei einem Modellwechsel (Haiku statt Sonnet) weißt du nicht, was safe ist zu kürzen
- Session-Ende = alles vergessen. Nächster Agent fängt von vorne an
- Zwei parallele Agents blockieren sich, weil keiner weiß, was der andere gerade anfasst

### Was .ctx konkret löst

| Situation | Ohne .ctx | Mit .ctx |
|-----------|-----------|----------|
| Agent dispatchen auf Modul X | Prompt von Hand schreiben | `LIES: .ctx/.distilled/haiku/X.ctx.md` |
| Haiku auf komplexem Code | Halluziniert Dependencies | Bekommt nur Signaturen + Invarianten |
| Sonnet auf Architektur-Task | Liest 40 Dateien, kostet $$ | Bekommt 1 Distillate mit vollem API |
| Opus auf tiefer Analyse | Nimmt sich alles, überschreitet Context | Bekommt exakt das richtige Tier |
| Session wechselt (anderer Tag) | Neuer Agent kennt nichts | `knowledge/LATEST.yaml` trägt die Learnings |
| 2 parallele Agents | Gegenseitige Überraschungen | Jeder hat seinen Modul-Scope klar |
| Neue Invariante entdeckt | Nirgends festgehalten | In .ctx.md + in Distillate — persistent |

### Gemessene Zahlen (Trade2, Produktionsprojekt)

```
313 Python-Quelldateien
451 .ctx.md-Dateien (inkl. externe Libs)

→ distilled auf 31 Dateien pro Tier:
  haiku:  ~34k Tokens  → Haiku sieht das GESAMTE System
  sonnet: ~49k Tokens  → Sonnet sieht Full API + Patterns
  opus:   ~89k Tokens  → Opus sieht alles inkl. Rationale

Kompression: 451 Dateien → 31 Distillate = 14:1
```

Ein Haiku-Agent bekommt mit 34k Tokens ein vollständiges Bild des gesamten Systems.
Ohne Distillation würde das gleiche Wissen ~300k Tokens kosten — oder 90% wären
einfach nicht drin.

---

## KRITISCH: Was fehlt, bevor das System wirklich funktioniert

Das Template ist ein Skelett. Auf einem neuen Projekt fehlen **fünf Dinge**,
ohne die Agents systematisch schlechte Ergebnisse liefern:

### 1. KRITISCH — INDEX.md auf dein Projekt zeigt

Die `INDEX.md` ist das erste, was jeder Agent liest. Wenn sie noch Template-Inhalte
hat, navigiert der Agent ins Leere.

**Was fehlt:** Die Modul-Tabelle muss deine echten Pakete zeigen, die Critical
Invariants müssen deine echten Grenzen beschreiben, die Tier-Regeln müssen zu
deiner Modell-Auswahl passen.

### 2. KRITISCH — CROSS_INDEX.json bildet echte Dependencies ab

Das ist die Maschinen-lesbare Dependency-Map. Wenn sie falsch ist, schickt jeder
Dispatch den Agent in die falsche Richtung.

**Was fehlt:** Jedes Modul mit seinen echten `depends_on` / `depended_by` / `provides`.
Kein Raten — direkt aus `import`-Statements ableiten.

### 3. KRITISCH — Modul .ctx.md existiert für jeden echten Package

Ohne `.ctx.md` pro Paket gibt es keine Distillation, keine Tier-Filterung, kein
`LIES ZUERST` für Agents. Das Paket ist eine Blackbox.

**Was fehlt:** Mindestens `## Purpose`, `## Public API`, `## Invariants` für jedes
Package das ein Agent anfassen wird. Ohne diese drei Sections ist ein Dispatch auf
das Modul schlechter als kein Dispatch.

### 4. KRITISCH — CLAUDE.md (oder AGENTS.md) enthält die Dispatch-Regel

Ohne diese Regel weißt du als Claude/Copilot nicht, dass `.ctx` existiert. Jeder
Agent startet blind.

**Was fehlt:** Die Dispatch-Regel muss in `CLAUDE.md` deines Projekts stehen,
nicht nur in diesem Template.

### 5. MITTEL — Distilled wurden nach jeder .ctx-Änderung neu gebaut

Veraltete Distillate sind schlimmer als keine Distillate — ein Agent der
`src/payments/processor.py` geändert hat, arbeitet gegen Distillate die noch den
alten Stand zeigen.

**Was fehlt:** Entweder ein pre-commit-Hook oder die Disziplin, nach jeder
`.ctx.md`-Änderung `build_distilled.py` zu laufen.

---

## Anleitung: Erstmalige Einrichtung auf einem neuen Projekt

### Phase 1 — Struktur aufsetzen (einmalig, ~30 Min)

```bash
# 1. Repo als .ctx/ in dein Projekt kopieren
cp -r ctx-repo/ /dein/projekt/.ctx/

# 2. Template-Beispieldateien löschen
rm .ctx/modules/example.ctx.md
rm .ctx/architecture/example_pattern.ctx.md

# 3. Verzeichnisse anlegen
mkdir -p .ctx/modules
mkdir -p .ctx/architecture
mkdir -p .ctx/knowledge/archive
```

### Phase 2 — INDEX.md auf dein Projekt anpassen (einmalig, ~20 Min)

`.ctx/INDEX.md` ist die einzige Datei, die jeder Agent immer liest.
Mach sie präzise.

```markdown
# MeinProjekt — Agent Entry Point

> Kurzbeschreibung: Was macht das Projekt? (1-2 Sätze)

## Quick Navigation

| Aufgabe | Lies zuerst |
|---------|------------|
| Verstehe Datenfluss | modules/pipeline.ctx.md |
| Ändere API | modules/api.ctx.md |
| Ändere Datenbank | modules/infra.ctx.md |

## Tier Selection

| Modell | Lies aus |
|--------|---------|
| Haiku | .ctx/.distilled/haiku/ |
| Sonnet | .ctx/.distilled/sonnet/ |
| Opus | .ctx/.distilled/opus/ + modules/ |

## Critical Invariants

1. Nur deine echte #1 Invariante
2. Nur deine echte #2 Invariante
...
```

**Keine Platzhalter.** Wenn du eine Invariante nicht kennst, lass sie weg.
Falsche Invarianten sind aktiv schädlich.

### Phase 3 — CROSS_INDEX.json aus echten Imports ableiten (einmalig, ~15–45 Min)

**Python-Projekte: automatisch via `ctx_scan.py`**

```bash
# 1. CTX_CONFIG.yaml anpassen (Source-Dir und Pakete)
cp CTX_CONFIG.yaml .ctx/CTX_CONFIG.yaml
# → source_dir und internal_packages eintragen

# 2. Scan laufen — erzeugt CROSS_INDEX.json + CTX_IR.jsonl + ANOMALIES.json
python scripts/ctx_scan.py
```

**Andere Sprachen: manuell**

```bash
# Imports analysieren (Beispiel für JS/TS)
grep -r "^import\|^require" src/ | grep -v node_modules | \
  sort | uniq -c | sort -rn | head -50
```

Dann CROSS_INDEX.json befüllen:

```json
{
  "modules": {
    "mein_paket": {
      "depends_on": ["infra", "common"],
      "depended_by": ["api", "workers"],
      "provides": ["MeineKlasse", "meine_funktion"],
      "entry_point": "modules/mein_paket.ctx.md"
    }
  }
}
```

**Regel:** `provides` = öffentliche API die andere Module nutzen.
`depends_on` = direkte Imports (keine transitiven).

### Phase 4 — Pro Paket ein .ctx.md erstellen (Hauptarbeit, ~1–2 Min/Paket)

Priorität: Pakete die Agents am häufigsten anfassen. Fang mit den stabilen Kern-Paketen an.

Mindest-Template für ein neues Modul:

```markdown
---
module: modules/mein_paket
type: codebase
depends_on: [infra, common]
depended_by: [api, workers]
provides: [MeineKlasse, meine_funktion]
invariants:
  - "Invariante 1 — nie verletzen"
  - "Invariante 2 — nie verletzen"
keywords: [relevante, begriffe]

tags: [ctx/module]
---

## Purpose  <!-- all-tiers -->

Was macht dieses Paket? Für wen? Warum existiert es?

## Public API  <!-- all-tiers -->

| Export | Typ | Zweck |
|--------|-----|-------|
| `MeineKlasse` | class | ... |
| `meine_funktion` | fn | ... |

## Invariants  <!-- all-tiers -->

1. Invariante 1 — Begründung
2. Invariante 2 — Begründung

## Key Patterns  <!-- sonnet+ -->

Wie wird das Paket typischerweise genutzt? Code-Beispiel.

## Design Rationale  <!-- opus-only -->

Warum wurde es so designt? Was wurde verworfen?

## Cross-References  <!-- all-tiers -->

- [[modules/infra.ctx|infra]] — warum diese Dependency
- [[modules/common.ctx|common]] — warum diese Dependency
```

**Tier-Tags sind Pflicht.** Jede Section muss `<!-- all-tiers -->`,
`<!-- sonnet+ -->` oder `<!-- opus-only -->` haben — sonst erscheint sie
in allen Tiers oder gar nicht.

### Phase 5 — Distillation bauen und prüfen (einmalig + nach jeder Änderung)

```bash
# Manuell nach Änderungen:
python scripts/build_distilled.py

# Python-Projekte: alles in einem Schritt (Scan + Frontmatter-Update + Distillation)
python scripts/ctx_autoregen.py

# Konsistenz prüfen (bidirectionality + CROSS_INDEX alignment):
python scripts/ctx_validate.py

# Prüfen: Macht das Haiku-Distillate Sinn?
cat .ctx/.distilled/haiku/mein_paket.ctx.md

# Token-Überblick
python -c "
import json
m = json.load(open('.ctx/.distilled/MANIFEST.json'))
for tier, data in m['tiers'].items():
    print(f'{tier}: {data[\"files\"]} files, ~{data[\"total_tokens\"]:,} tokens')
"
```

**Zielgrößen:**
- Haiku-Tier: < 40k Tokens gesamt (Haiku-Kontextfenster nutzen ohne zu verschwenden)
- Sonnet-Tier: < 80k Tokens gesamt
- Opus-Tier: Kein hartes Limit, aber > 200k ist ein Zeichen für Redundanz

### Phase 6 — Dispatch-Regel in CLAUDE.md eintragen (einmalig, 5 Min)

In dein `CLAUDE.md` / `AGENTS.md` einfügen:

```markdown
## Kontext-Distillation (Pflicht für ALLE Agent-Dispatches)

Beim Dispatchen eines Sub-Agents:
1. Bestimme welche Module der Agent bearbeitet
2. Füge in den Prompt ein:
   - Haiku: "LIES ZUERST: .ctx/.distilled/haiku/{modul}.ctx.md"
   - Sonnet: "LIES ZUERST: .ctx/.distilled/sonnet/{modul}.ctx.md"
   - Opus: "LIES ZUERST: .ctx/.distilled/opus/{modul}.ctx.md"
3. Bei Architektur-Aufgaben zusätzlich relevante Architecture-Docs

### Modul-Mapping

| Package | .ctx Datei |
|---------|-----------|
| mein_paket/ | mein_paket.ctx.md |
| anderes_paket/ | anderes_paket.ctx.md |
```

---

## Anleitung: Kontinuierliche Nutzung

Nach der Ersteinrichtung gibt es **drei Trigger** für .ctx-Arbeit:

### Trigger 1 — Du änderst öffentliche API eines Pakets

```
Geänderte Datei → .ctx.md des Pakets updaten → build_distilled.py laufen
```

Konkret: Wenn du eine neue Funktion in `src/api/users.py` hinzufügst, die andere
Module nutzen werden:
1. `modules/api.ctx.md` — Public API-Tabelle updaten
2. `CROSS_INDEX.json` — falls neue `provides`
3. `python scripts/build_distilled.py`

**Faustregel:** `## Public API` und `## Invariants` müssen immer aktuell sein.
`## Design Rationale` darf veralten — es ist historisch.

### Trigger 2 — Du entdeckst eine neue Invariante oder eine bricht

Das ist der wichtigste Moment. Invarianten in `.ctx.md` sind der einzige Weg,
wie zukünftige Agents von vergangenen Fehlern lernen.

```markdown
## Invariants  <!-- all-tiers -->

1. Feature-Spaltennamen nur via contract.yaml ändern — nie direkt in Code
   (Invariante 3 verletzt → 4h Debugging, 2024-03-15)
2. Neue Invariante: ...
```

Nach dem Eintragen: `build_distilled.py` laufen, damit die Invariante im
Haiku-Tier (dem wichtigsten für Agents) landet.

### Trigger 3 — Session-Ende / Handoff an anderen Agent

```bash
python scripts/new_knowledge.py "Was der nächste Agent angehen soll"
```

Das legt `.ctx/knowledge/LATEST.yaml` an. Was da rein muss:

```yaml
milestone: "Was jetzt wahr ist, was vorher nicht wahr war"

cross_session_patterns:
  - discovery: "Nicht-offensichtliche Erkenntnis"
    applies_to: [modul_a, modul_b]
    # Wenn sich zwei Module gegenseitig importieren -> Deadlock. Immer via Bus.

next_session_hints:
  - priority: 1
    task: "Was als nächstes getan werden muss"
    context: ".ctx/.distilled/sonnet/relevantes_modul.ctx.md"

open_items:
  - item: "Bewusst aufgeschoben"
    why_deferred: "Konkreter Grund"
    trigger: "Wann wieder aufgreifen"
```

**Was NICHT rein soll:** Welche Dateien geändert wurden (git log), wie eine
Funktion funktioniert (Code lesen), was heute gemacht wurde (git blame).

---

## Cross-Referenzen aufbauen — das unterschätzte Feature

Cross-Referenzen in `.ctx.md` sind keine Dekoration. Sie sind die einzige
Möglichkeit, wie ein Agent weiß, **wohin er als nächstes schauen muss**,
ohne alle Dateien zu lesen.

### Schlechte Cross-Referenz (nutzlos)

```markdown
## Cross-References
- infra/ — Infrastruktur
- common/ — Utilities
```

### Gute Cross-Referenz (nützlich)

```markdown
## Cross-References  <!-- all-tiers -->

- [[modules/db.ctx|db]] — Datenbankverbindung, die api/ nutzt für Queries
- [[modules/auth.ctx|auth]] — JWT-Validation muss vor jedem API-Handler laufen
- [[modules/workers.ctx|workers]] — Async-Jobs werden über workers/ dispatcht, nie direkt
- [[architecture/API_CONTRACT.ctx|API_CONTRACT]] — warum Payload-Schema nur via schema.py änderbar
```

**Regel:** Jede Cross-Referenz braucht ein "warum" — sonst ist sie nutzlos.
Ein Agent der weiß "features hängt von signals ab — weil Feature-Output über den
Bus geht, nicht direkt" kann korrekte Entscheidungen treffen. Einer der nur weiß
"features hängt von signals ab" nicht.

### CROSS_INDEX.json korrekt halten

```bash
# Prüfen ob CROSS_INDEX.json vollständig ist
python -c "
import json
with open('.ctx/CROSS_INDEX.json') as f:
    ci = json.load(f)
modules = set(ci['modules'].keys())
for name, data in ci['modules'].items():
    for dep in data.get('depends_on', []):
        if dep not in modules:
            print(f'FEHLT: {name}.depends_on enthält {dep}, aber {dep} hat kein Modul-Eintrag')
"
```

---

## Checkliste: Vollständige Funktionsfähigkeit

### Ersteinrichtung abgeschlossen wenn:

```
[ ] .ctx/ liegt im Projekt-Root (nicht irgendwo anders)
[ ] INDEX.md zeigt echte Module, keine Template-Platzhalter
[ ] CROSS_INDEX.json hat alle Pakete mit echten depends_on/provides
[ ] Jedes Paket das Agents anfassen werden hat ein .ctx.md
[ ] Jedes .ctx.md hat Tier-Tags (<!-- all-tiers -->, <!-- sonnet+ -->, etc.)
[ ] Jedes .ctx.md hat mindestens: Purpose, Public API, Invariants
[ ] build_distilled.py läuft ohne Fehler durch
[ ] Haiku-Distillate sehen sinnvoll aus (nicht leer, nicht zu groß)
[ ] Dispatch-Regel steht in CLAUDE.md / AGENTS.md des Projekts
[ ] Ein Test-Dispatch auf ein Modul wurde gemacht und Agent hatte richtigen Kontext
```

### Kontinuierliche Nutzung gesund wenn:

```
[ ] build_distilled.py läuft nach jeder .ctx.md-Änderung
[ ] Neue Invarianten werden sofort in .ctx.md eingetragen (nicht "später")
[ ] Session-Ende: knowledge/LATEST.yaml ist aktuell
[ ] Public API Änderungen → .ctx.md Public API Tabelle sofort geupdatet
[ ] CROSS_INDEX.json spiegelt echte Dependencies (kein Drift)
[ ] Distillate sind nie älter als die Quelle (MANIFEST.json Timestamp prüfen)
```

---

## Häufige Fehler

### Fehler 1 — .ctx.md ohne Tier-Tags

```markdown
## Design Rationale
Warum dieses Design...
```

**Problem:** Section erscheint in allen Tiers. Haiku bekommt Design-Rationale
die es nicht braucht und bezahlt dafür in Tokens.

**Fix:** Immer taggsen:
```markdown
## Design Rationale  <!-- opus-only -->
```

### Fehler 2 — Distillate nicht nach Änderung neu gebaut

**Problem:** Agent liest `.ctx/.distilled/haiku/features.ctx.md` und sieht
einen Monat alten Stand. Arbeitet gegen veraltete Invarianten.

**Fix:** `build_distilled.py` in pre-commit-Hook oder als Makefile-Target.

```bash
# .git/hooks/pre-commit
#!/bin/bash
cd .ctx && python scripts/build_distilled.py --quiet
git add .ctx/.distilled/
```

### Fehler 3 — CROSS_INDEX.json nie geupdatet

**Problem:** Ein neues Paket wird hinzugefügt, taucht nie in CROSS_INDEX.json
auf. Agents wissen nicht, dass es existiert oder was es tut.

**Fix:** CROSS_INDEX.json ist Teil des Definition-of-Done für jedes neue Paket.

### Fehler 4 — knowledge/LATEST.yaml bleibt leer

**Problem:** Nächste Session fängt von vorne an. Alle Learnings, Patterns,
offenen Punkte sind weg.

**Fix:** `new_knowledge.py` läuft am Ende jeder signifikanten Session.

### Fehler 5 — Invarianten im .ctx.md veralten

**Problem:** Code hat sich geändert, Invariante gilt nicht mehr, steht aber
noch im Distillate. Agent hält sich an eine falsche Invariante.

**Fix:** Invarianten sind das erste, was beim Refactoring geprüft wird.
Wenn eine Invariante bricht, muss sie sofort aus .ctx.md raus (oder angepasst).

---

## Navigation

[[INDEX]] · [[OBSIDIAN]] · [[README]] · [[CLAUDE]] · [[AGENTS]] · [[modules/example.ctx|example module]] · [[architecture/example_pattern.ctx|example pattern]] · [[examples/openclaw/INDEX|OpenClaw example]]
