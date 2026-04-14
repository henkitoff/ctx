🇬🇧 English · [🇩🇪 Deutsch](INDEX.de.md)

# Project Index — Agent Entry Point

> **Every agent starts here.** This file routes to the right context
> for any task. Read this first, then follow the links.

---

## Quick Navigation

<!-- Fill this table with your actual modules and tasks -->

| Task | Read first |
|------|-----------|
| Understand module X | [[modules/example.ctx\|example module]] (template) |
| Understand a cross-cutting pattern | [[architecture/example_pattern.ctx\|example pattern]] (template) |
| All architecture patterns | [[architecture/INDEX\|architecture index]] |
| Set up Obsidian for humans + agents | [[OBSIDIAN]] |
| Full setup guide | [[GUIDE]] |
| Real-world full example | [[examples/openclaw/INDEX\|OpenClaw example]] |

---

## Tier Selection

Choose the distilled version that matches your model:

| Model | Read from |
|-------|-----------|
| Haiku / fast workers | .distilled/haiku/ |
| Sonnet / manager agents | .distilled/sonnet/ |
| Opus / architect tasks | modules/ + architecture/ |

---

## Critical Invariants

> These apply to every agent, every task, no exceptions.

1. <!-- Add your project's hard invariants here -->
2. <!-- e.g. "No direct DB access outside the repository layer" -->
3. <!-- e.g. "All secrets via environment variables, never in code" -->

---

## Module Overview

<!-- Auto-updated by scripts/build_distilled.py -->

| Module | Provides | Depends on |
|--------|---------|------------|
| example | (see .distilled/opus/example.ctx.md) |  |
## Last Session (Knowledge Distillate)

Agents read `knowledge/LATEST.yaml` at session start to understand current state.

```
knowledge/
├── LATEST.yaml          ← Always read this — current project state
├── TEMPLATE.yaml        ← Copy this when creating a new distillate
└── archive/             ← Past distillates (auto-archived by script)
```

To start a new session distillate:
```bash
python scripts/new_knowledge.py "What you plan to work on"
```

---

## Navigation

[[GUIDE]] · [[OBSIDIAN]] · [[README]] · [[CLAUDE]] · [[AGENTS]] · [[architecture/INDEX|Architecture]] · [[modules/example.ctx|example module]] · [[examples/openclaw/INDEX|OpenClaw example]]
