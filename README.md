# .ctx — Agent Knowledge Graph Template

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A project-agnostic knowledge graph structure that makes any codebase navigable
for AI agents (Claude, Copilot, Codex, GPT-4) — without replacing human docs.

**→ [GUIDE.md](GUIDE.md) — vollständige Setup-Anleitung + kontinuierliche Nutzung**

## Why this exists

Without `.ctx`, every agent starts from zero. It either reads too little
(hallucinates) or too much (costs a fortune). With `.ctx`, each model gets
exactly what it needs for its task — nothing more, nothing less.

| Problem | Without .ctx | With .ctx |
|---------|-------------|----------|
| Agent dispatched to module X | Write context by hand every time | `READ FIRST: .ctx/.distilled/haiku/X.ctx.md` |
| Haiku on complex code | Hallucinates dependencies | Gets only signatures + invariants |
| Sonnet on architecture task | Reads 40 files, costs $$ | Gets 1 distillate with full API |
| Session ends / new agent | Everything forgotten | `knowledge/LATEST.yaml` carries the learnings |
| 2 parallel agents | Surprise collisions | Each has their module scope explicit |
| New invariant discovered | Written nowhere | In .ctx.md + in distillate — persistent across sessions |

**Measured numbers (production project):**
```
451 source .ctx.md files → 31 distilled per tier = 14:1 compression

.distilled/haiku/:  ~34k tokens  → Haiku sees the ENTIRE system
.distilled/sonnet/: ~49k tokens  → Sonnet sees full API + patterns
.distilled/opus/:   ~89k tokens  → Opus sees everything incl. rationale
```

## What's missing before this works on your project

Five things — without these, agents deliver systematically bad results:

- **CRITICAL** `INDEX.md` must reflect your real modules, not template placeholders
- **CRITICAL** `CROSS_INDEX.json` must map your real import dependencies
- **CRITICAL** One `.ctx.md` per package agents will touch (min: Purpose + API + Invariants)
- **CRITICAL** Dispatch rule in your project's `CLAUDE.md` / `AGENTS.md`
- **IMPORTANT** Rebuild `.distilled/` after every `.ctx.md` change (stale distillates are worse than none)

**→ [GUIDE.md](GUIDE.md) has the step-by-step for all of these.**

## Quick start

```bash
# 1. Copy into your project
cp -r ctx-repo/ /your/project/.ctx/

# 2. Remove template files
rm .ctx/modules/example.ctx.md .ctx/architecture/example_pattern.ctx.md

# 3. Configure (Python projects): edit .ctx/CTX_CONFIG.yaml
#    → set source_dir and internal_packages to match your project

# 4. Auto-scan imports + build distillates (Python)
cd .ctx/ && python scripts/ctx_scan.py && python scripts/build_distilled.py

# 5. Add dispatch rule to your CLAUDE.md — see GUIDE.md Phase 6
```

## Structure

```
.ctx/
├── INDEX.md                 ← Agent entry point (always read first)
├── CROSS_INDEX.json         ← Machine-readable dependency graph
├── CTX_CONFIG.yaml          ← Build config (source_dir, packages, services)
│
├── modules/                 ← One .ctx.md per domain / package
│   └── example.ctx.md       ← Full annotated example
│
├── architecture/            ← Cross-cutting patterns & ADRs
│   ├── INDEX.md
│   └── example_pattern.ctx.md
│
├── .distilled/               ← Auto-generated tier versions
│   ├── MANIFEST.json        ← Token counts per file per tier
│   ├── haiku/               ← ~25k tokens: signatures + invariants only
│   ├── sonnet/              ← ~50k tokens: full API + patterns
│   └── opus/                ← ~90k tokens: everything incl. rationale
│
├── knowledge/               ← Knowledge distillates (session handoffs)
│   ├── LATEST.yaml          ← Agents read this at session start
│   ├── TEMPLATE.yaml        ← Copy to create a new distillate
│   └── archive/             ← Past distillates (auto-archived)
│
└── scripts/
    ├── build_distilled.py   ← Tier distillation (run after any .ctx.md change)
    ├── ctx_scan.py          ← AST-based CROSS_INDEX auto-generator (Python)
    ├── ctx_autoregen.py     ← Incremental .ctx.md updater (mtime-based)
    ├── ctx_validate.py      ← Bidirectionality + consistency checker
    ├── _ctx_common.py       ← Shared helpers (imported by other scripts)
    └── new_knowledge.py     ← Create new knowledge distillate
```

## Two types of distillation

This template combines two distinct distillation mechanisms:

### 1. Code distillation → `.distilled/`

Tier-filtered versions of module docs. Build with:
```bash
python scripts/build_distilled.py
```

Rebuild is needed after any `.ctx.md` change. Stale distillates are worse than none.

### 2. Knowledge distillation → `knowledge/`

Session handoffs: decisions made, patterns learned, next hints.
Agents read `knowledge/LATEST.yaml` at session start. Create with:
```bash
python scripts/new_knowledge.py "What you plan to work on"
```

The script:
- Pre-fills `date` and `topic`
- Archives the previous `LATEST.yaml` to `knowledge/archive/YYYY-MM-DD_topic.yaml`
- Opens a fresh `LATEST.yaml` ready to fill in

**What goes in a knowledge distillate:**
- `milestone` — what is now true that wasn't before
- `cross_session_patterns` — non-obvious learnings future agents must know
- `next_session_hints` — ordered priorities
- `open_items` — conscious deferrals with explicit `why_deferred`

**What does NOT go in:**
- What files changed (use `git log`)
- How a function works (read the code)
- Anything derivable from current codebase state

## Tier system

Every `.ctx.md` file uses HTML comment tags to mark sections for specific tiers:

```markdown
## Purpose  <!-- all-tiers -->
Visible to all agents — keep concise.

## Key Patterns  <!-- sonnet+ -->
Only Sonnet and Opus agents see this.

## Design Rationale  <!-- opus-only -->
Only Opus sees this. Full context, trade-offs, history.
```

Run `scripts/build_distilled.py` after editing any module file.

## Automation scripts

For Python projects, three automation scripts are available:

```bash
# 1. Auto-generate CROSS_INDEX.json from real imports (AST-based)
python scripts/ctx_scan.py

# 2. Incremental update: refresh stale .ctx.md frontmatter + rebuild distillates
python scripts/ctx_autoregen.py

# 3. Consistency check: bidirectionality + CROSS_INDEX alignment
python scripts/ctx_validate.py
```

These scripts read their configuration from `.ctx/CTX_CONFIG.yaml`.
Copy `CTX_CONFIG.yaml` (root of this repo) to `.ctx/CTX_CONFIG.yaml` in your project and adapt it.

## Agent dispatch rule

Add to your `CLAUDE.md` / `AGENTS.md`:

```
Before any agent dispatch, include the right tier context:
- Haiku / fast worker  → .ctx/.distilled/haiku/{module}.ctx.md
- Sonnet / manager     → .ctx/.distilled/sonnet/{module}.ctx.md
- Opus / architect     → .ctx/modules/{module}.ctx.md + .ctx/architecture/
```

## Real-world example: openclaw

`examples/openclaw/` contains a complete `.ctx` for
[openclaw/openclaw](https://github.com/openclaw/openclaw) — a TypeScript
AI assistant gateway with 6 500 source files and 99 plugins.

```
examples/openclaw/
├── INDEX.md              ← Agent entry point with full module map
├── CROSS_INDEX.json      ← Dependency graph (15+ modules + 8 architecture entries)
├── modules/              ← 15 module docs (gateway, agents, memory, hooks, sessions, …)
├── architecture/         ← 9 cross-cutting docs (multi-agent, runtime, sandbox, …)
└── .distilled/            ← haiku: ~21k tokens · sonnet: ~36k · opus: ~39k
```

Build the openclaw distillates:
```bash
python scripts/build_distilled.py --project openclaw
```

## Examples

Named projects live under `examples/<name>/` and use the same structure as the
root template. Build any example with:
```bash
python scripts/build_distilled.py --project <name>
```

## Obsidian integration

`OBSIDIAN.md` explains how to open this repo as an Obsidian vault (or add it as
a subfolder to an existing vault) so the same files serve both humans and agents:

- Frontmatter → Obsidian Properties panel
- Tier tags → invisible in render, machine-readable by agents
- `CROSS_INDEX.json` → agent dependency graph; Canvas → human equivalent
- `knowledge/LATEST.yaml` → pinned vault home + agent session handoff
- Dataview queries → auto-generated module tables (no manual maintenance)
- Templater templates in `obsidian/templates/` for consistent module creation

Quick start: open `OBSIDIAN.md`, follow the 15-minute one-time setup checklist.

## Real-world example: production scale

A large production codebase built entirely on this `.ctx` structure.

**The numbers:**

| | |
|---|---|
| Python source files | 313 |
| Source `.ctx.md` files | 275 |
| Coverage | ~1:1 — nearly every `.py` has its `.ctx.md` |
| External library docs | 176 (API references, framework docs, …) |
| Total source `.ctx.md` | 451 |

**Distillation — 451 files collapsed to 31 per tier:**

| Tier | Files | Tokens | Used for |
|------|-------|--------|----------|
| haiku | 31 | ~34k | Fast workers, rule-based agents |
| sonnet | 31 | ~49k | Manager agents, most agent dispatches |
| opus | 31 | ~89k | Architect tasks, cross-module analysis |

**Compression: 451 source files → 31 distilled files = 14:1**

The `.ctx` covers the full stack:

```
.ctx/
├── src/             ← 275 files, mirrors project source 1:1
│   ├── core/        ← domain core modules
│   ├── services/    ← service layer
│   ├── infra/       ← infrastructure adapters
│   └── …
├── architecture/    ← ADRs + design decisions
├── external/        ← third-party API references + library docs
└── .distilled/      ← haiku / sonnet / opus tiers, auto-generated
```

The key insight: at this scale the distilled tier (31 files, ~34–89k tokens
depending on model) gives every agent a complete picture of the entire system
without blowing the context window. The 1:1 source coverage means no module
is a black box.

## License

MIT — use freely, adapt to your project.

---

## Navigation

[[INDEX]] · [[GUIDE]] · [[OBSIDIAN]] · [[CLAUDE]] · [[AGENTS]] · [[modules/example.ctx|example module]] · [[architecture/example_pattern.ctx|example pattern]] · [[examples/openclaw/INDEX|OpenClaw example]]
