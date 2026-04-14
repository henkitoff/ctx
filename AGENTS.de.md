[🇬🇧 English](AGENTS.md) · 🇩🇪 Deutsch

# Agenten-Einstiegspunkt (Codex / GitHub Copilot)

Hier starten. Zuerst INDEX.md lesen, dann der Aufgaben-Tabelle folgen.

## Dispatch-Regeln

- Vor der Arbeit immer den tier-passenden destillierten Kontext laden
- `.ctx`-Kontext bei nicht-trivialen Änderungen nie überspringen
- Vor dem Ändern eines Moduls CROSS_INDEX.json auf Abhängigkeits-Impact prüfen

## Tier-Auswahl

- Haiku / schnelle Worker    → .distilled/haiku/{modul}.ctx.md
- Sonnet / Manager-Agenten  → .distilled/sonnet/{modul}.ctx.md
- Opus / Architektur-Aufgaben → modules/{modul}.ctx.md

## Kritische Invarianten

Siehe [[INDEX.de]] → Abschnitt „Kritische Invarianten".

---

## Navigation

[[INDEX.de]] · [[CLAUDE]] · [[GUIDE.de]] · [[OBSIDIAN.de]] · [[modules/example.ctx|Beispiel-Modul]] · [[examples/openclaw/INDEX|OpenClaw-Beispiel]]
