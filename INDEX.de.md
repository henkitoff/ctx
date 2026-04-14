[🇬🇧 English](INDEX.md) · 🇩🇪 Deutsch

# Projekt-Index — Agenten-Einstiegspunkt

> **Jeder Agent startet hier.** Diese Datei leitet zum richtigen Kontext
> für jede Aufgabe. Zuerst diese Datei lesen, dann den Links folgen.

---

## Schnellnavigation

<!-- Mit deinen echten Modulen und Aufgaben befüllen -->

| Aufgabe | Zuerst lesen |
|---------|-------------|
| Modul X verstehen | [[modules/example.ctx\|Beispiel-Modul]] (Template) |
| Übergreifendes Muster verstehen | [[architecture/example_pattern.ctx\|Beispiel-Muster]] (Template) |
| Alle Architektur-Muster | [[architecture/INDEX\|Architektur-Index]] |
| Obsidian für Menschen + Agenten einrichten | [[OBSIDIAN.de]] |
| Vollständiger Setup-Guide | [[GUIDE.de]] |
| Vollständiges Praxisbeispiel | [[examples/openclaw/INDEX\|OpenClaw-Beispiel]] |

---

## Tier-Auswahl

Die passende destillierte Version für dein Modell wählen:

| Modell | Lies aus |
|--------|---------|
| Haiku / schnelle Worker | .distilled/haiku/ |
| Sonnet / Manager-Agenten | .distilled/sonnet/ |
| Opus / Architektur-Aufgaben | modules/ + architecture/ |

---

## Kritische Invarianten

> Diese gelten für jeden Agenten, jede Aufgabe, ohne Ausnahmen.

1. <!-- Deine harten Projektinvarianten hier eintragen -->
2. <!-- z. B. „Kein direkter DB-Zugriff außerhalb der Repository-Schicht" -->
3. <!-- z. B. „Alle Secrets via Umgebungsvariablen, nie im Code" -->

---

## Modul-Übersicht

<!-- Automatisch aktualisiert durch scripts/build_distilled.py -->

| Modul | Stellt bereit | Hängt ab von |
|-------|--------------|--------------|
| example | (siehe .distilled/opus/example.ctx.md) | |

---

## Letzte Session (Knowledge-Distillat)

Agenten lesen `knowledge/LATEST.yaml` zu Session-Beginn.

```
knowledge/
├── LATEST.yaml          ← Immer zuerst lesen — aktueller Projektstatus
├── TEMPLATE.yaml        ← Kopieren für neues Distillat
└── archive/             ← Vergangene Distillate
```

Neues Session-Distillat starten:
```bash
python scripts/new_knowledge.py "Woran du arbeiten möchtest"
```

---

## Navigation

[[GUIDE.de]] · [[OBSIDIAN.de]] · [[README]] · [[CLAUDE]] · [[AGENTS]] · [[architecture/INDEX|Architektur]] · [[modules/example.ctx|Beispiel-Modul]] · [[examples/openclaw/INDEX|OpenClaw-Beispiel]]
