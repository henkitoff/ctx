[🇬🇧 English](CLAUDE.md) · 🇩🇪 Deutsch

# Agenten-Dispatch-Regeln

> Den relevanten Abschnitt in die `CLAUDE.md` / `AGENTS.md` deines Projekts kopieren.

---

## Kontext-Distillation (Pflicht für ALLE Agenten-Dispatches)

Vor dem Dispatchen eines Sub-Agenten oder dem Start einer Aufgabe:

1. Bestimmen, an welchen Modulen der Agent arbeiten wird
2. Den richtigen Tier-Kontext in den Prompt aufnehmen:
   - Haiku / schnelle Worker:    „LIES ZUERST: .ctx/.distilled/haiku/{modul}.ctx.md"
   - Sonnet / Manager-Agenten:  „LIES ZUERST: .ctx/.distilled/sonnet/{modul}.ctx.md"
   - Opus / Architektur-Aufgaben: „LIES ZUERST: .ctx/modules/{modul}.ctx.md"
3. Bei Architektur-Aufgaben zusätzlich .ctx/architecture/ einbeziehen

Kein Agenten-Dispatch ohne passenden .ctx-Kontext.

---

## Modul-Mapping

<!-- Mit deinen echten Modulen befüllen -->

| Paket / Ordner | .ctx-Datei |
|----------------|-----------|
| src/example/   | modules/example.ctx.md |

---

## Ausnahmen (kein .ctx nötig)

- Reine Config-Änderungen (nur JSON/YAML)
- Dokumentations-Updates (.md-Dateien)
- Test-only-Änderungen, die keine neuen APIs nutzen

---

## Navigation

[[INDEX.de]] · [[AGENTS.de]] · [[GUIDE.de]] · [[OBSIDIAN.de]] · [[modules/example.ctx|Beispiel-Modul]] · [[examples/openclaw/INDEX|OpenClaw-Beispiel]]
