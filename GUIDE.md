🇬🇧 English · [🇩🇪 Deutsch](GUIDE.de.md)

# .ctx — Complete Setup and Usage Guide

---

## Why .ctx + Distillation? The Real Advantage

Without `.ctx`, every agent starts from zero — it either reads too little (hallucinates)
or too much (costs a fortune). With `.ctx`, every model has exactly the information
it needs for its task. No more. No less.

### The Core Problem Without .ctx

An agent working on a 300-file project:
- Reads 10 random files and hallucinates the rest
- Or you write the context by hand into every prompt — every single time
- When switching models (Haiku instead of Sonnet) you don't know what is safe to cut
- Session ends = everything forgotten. The next agent starts from scratch
- Two parallel agents block each other because neither knows what the other is currently touching

### What .ctx Concretely Solves

| Situation | Without .ctx | With .ctx |
|-----------|-------------|----------|
| Dispatch agent to module X | Write prompt by hand | `READ: .ctx/.distilled/haiku/X.ctx.md` |
| Haiku on complex code | Hallucinates dependencies | Gets only signatures + invariants |
| Sonnet on architecture task | Reads 40 files, costs $$ | Gets 1 distillate with full API |
| Opus on deep analysis | Takes everything, exceeds context | Gets exactly the right tier |
| Session switches (another day) | New agent knows nothing | `knowledge/LATEST.yaml` carries the learnings |
| 2 parallel agents | Mutual surprises | Each has their module scope clearly defined |
| New invariant discovered | Recorded nowhere | In .ctx.md + in distillate — persistent |

### Measured Numbers (production project)

```
313 Python source files
451 .ctx.md files (incl. external libs)

→ distilled to 31 files per tier:
  haiku:  ~34k tokens  → Haiku sees the ENTIRE system
  sonnet: ~49k tokens  → Sonnet sees full API + patterns
  opus:   ~89k tokens  → Opus sees everything incl. rationale

Compression: 451 files → 31 distillates = 14:1
```

A Haiku agent receives a complete picture of the entire system with 34k tokens.
Without distillation, the same knowledge would cost ~300k tokens — or 90% simply
would not be included.

---

## CRITICAL: What Is Missing Before the System Actually Works

The template is a skeleton. On a new project, **five things** are missing
without which agents will systematically deliver poor results:

### 1. CRITICAL — INDEX.md Points to Your Project

`INDEX.md` is the first thing every agent reads. If it still contains template
content, the agent navigates into a void.

**What is missing:** The module table must show your real packages, the Critical
Invariants must describe your real boundaries, the tier rules must match your
model selection.

### 2. CRITICAL — CROSS_INDEX.json Maps Real Dependencies

This is the machine-readable dependency map. If it is wrong, every dispatch
sends the agent in the wrong direction.

**What is missing:** Every module with its real `depends_on` / `depended_by` / `provides`.
No guessing — derive directly from `import` statements.

### 3. CRITICAL — Module .ctx.md Exists for Every Real Package

Without a `.ctx.md` per package there is no distillation, no tier filtering, no
`READ FIRST` for agents. The package is a black box.

**What is missing:** At minimum `## Purpose`, `## Public API`, `## Invariants` for every
package an agent will touch. Without these three sections, a dispatch to the module
is worse than no dispatch at all.

### 4. CRITICAL — CLAUDE.md (or AGENTS.md) Contains the Dispatch Rule

Without this rule, Claude/Copilot does not know that `.ctx` exists. Every
agent starts blind.

**What is missing:** The dispatch rule must be in your project's `CLAUDE.md`,
not only in this template.

### 5. MEDIUM — Distillates Were Rebuilt After Every .ctx Change

Outdated distillates are worse than no distillates — an agent that has changed
`src/payments/processor.py` is working against distillates that still show the
old state.

**What is missing:** Either a pre-commit hook or the discipline to run
`build_distilled.py` after every `.ctx.md` change.

---

## Guide: Initial Setup on a New Project

### Phase 1 — Set Up Structure (once, ~30 min)

```bash
# 1. Copy repo as .ctx/ into your project
cp -r ctx-repo/ /your/project/.ctx/

# 2. Delete template example files
rm .ctx/modules/example.ctx.md
rm .ctx/architecture/example_pattern.ctx.md

# 3. Create directories
mkdir -p .ctx/modules
mkdir -p .ctx/architecture
mkdir -p .ctx/knowledge/archive
```

### Phase 2 — Adapt INDEX.md to Your Project (once, ~20 min)

`.ctx/INDEX.md` is the only file every agent always reads.
Make it precise.

```markdown
# MyProject — Agent Entry Point

> Brief description: What does the project do? (1-2 sentences)

## Quick Navigation

| Task | Read first |
|------|-----------|
| Understand data flow | modules/pipeline.ctx.md |
| Change API | modules/api.ctx.md |
| Change database | modules/infra.ctx.md |

## Tier Selection

| Model | Read from |
|-------|----------|
| Haiku | .ctx/.distilled/haiku/ |
| Sonnet | .ctx/.distilled/sonnet/ |
| Opus | .ctx/.distilled/opus/ + modules/ |

## Critical Invariants

1. Only your real #1 invariant
2. Only your real #2 invariant
...
```

**No placeholders.** If you don't know an invariant, leave it out.
Wrong invariants are actively harmful.

### Phase 3 — Derive CROSS_INDEX.json from Real Imports (once, ~15–45 min)

**Python projects: automatically via `ctx_scan.py`**

```bash
# 1. Adapt CTX_CONFIG.yaml (source dir and packages)
cp CTX_CONFIG.yaml .ctx/CTX_CONFIG.yaml
# → enter source_dir and internal_packages

# 2. Run scan — generates CROSS_INDEX.json + CTX_IR.jsonl + ANOMALIES.json
python scripts/ctx_scan.py
```

**Other languages: manually**

```bash
# Analyze imports (example for JS/TS)
grep -r "^import\|^require" src/ | grep -v node_modules | \
  sort | uniq -c | sort -rn | head -50
```

Then populate CROSS_INDEX.json:

```json
{
  "modules": {
    "my_package": {
      "depends_on": ["infra", "common"],
      "depended_by": ["api", "workers"],
      "provides": ["MyClass", "my_function"],
      "entry_point": "modules/my_package.ctx.md"
    }
  }
}
```

**Rule:** `provides` = public API that other modules use.
`depends_on` = direct imports (no transitives).

### Phase 4 — Create One .ctx.md Per Package (main work, ~1–2 min/package)

Priority: packages that agents touch most often. Start with the stable core packages.

Minimum template for a new module:

```markdown
---
module: modules/my_package
type: codebase
depends_on: [infra, common]
depended_by: [api, workers]
provides: [MyClass, my_function]
invariants:
  - "Invariant 1 — never violate"
  - "Invariant 2 — never violate"
keywords: [relevant, terms]

tags: [ctx/module]
---

## Purpose  <!-- all-tiers -->

What does this package do? For whom? Why does it exist?

## Public API  <!-- all-tiers -->

| Export | Type | Purpose |
|--------|------|---------|
| `MyClass` | class | ... |
| `my_function` | fn | ... |

## Invariants  <!-- all-tiers -->

1. Invariant 1 — rationale
2. Invariant 2 — rationale

## Key Patterns  <!-- sonnet+ -->

How is the package typically used? Code example.

## Design Rationale  <!-- opus-only -->

Why was it designed this way? What was discarded?

## Cross-References  <!-- all-tiers -->

- [[modules/infra.ctx|infra]] — why this dependency
- [[modules/common.ctx|common]] — why this dependency
```

**Tier tags are mandatory.** Every section must have `<!-- all-tiers -->`,
`<!-- sonnet+ -->`, or `<!-- opus-only -->` — otherwise it appears in
all tiers or not at all.

### Phase 5 — Build and Verify Distillation (once + after every change)

```bash
# Manually after changes:
python scripts/build_distilled.py

# Python projects: everything in one step (scan + frontmatter update + distillation)
python scripts/ctx_autoregen.py

# Check consistency (bidirectionality + CROSS_INDEX alignment):
python scripts/ctx_validate.py

# Check: does the Haiku distillate make sense?
cat .ctx/.distilled/haiku/my_package.ctx.md

# Token overview
python -c "
import json
m = json.load(open('.ctx/.distilled/MANIFEST.json'))
for tier, data in m['tiers'].items():
    print(f'{tier}: {data[\"files\"]} files, ~{data[\"total_tokens\"]:,} tokens')
"
```

**Target sizes:**
- Haiku tier: < 40k tokens total (use Haiku context window without wasting it)
- Sonnet tier: < 80k tokens total
- Opus tier: No hard limit, but > 200k is a sign of redundancy

### Phase 6 — Add Dispatch Rule to CLAUDE.md (once, 5 min)

Add to your `CLAUDE.md` / `AGENTS.md`:

```markdown
## Context Distillation (Required for ALL Agent Dispatches)

When dispatching a sub-agent:
1. Determine which modules the agent will work on
2. Add to the prompt:
   - Haiku: "READ FIRST: .ctx/.distilled/haiku/{module}.ctx.md"
   - Sonnet: "READ FIRST: .ctx/.distilled/sonnet/{module}.ctx.md"
   - Opus: "READ FIRST: .ctx/.distilled/opus/{module}.ctx.md"
3. For architecture tasks, additionally include relevant architecture docs

### Module Mapping

| Package | .ctx file |
|---------|----------|
| my_package/ | my_package.ctx.md |
| other_package/ | other_package.ctx.md |
```

---

## Guide: Ongoing Usage

After the initial setup there are **three triggers** for .ctx work:

### Trigger 1 — You Change the Public API of a Package

```
Changed file → update .ctx.md of the package → run build_distilled.py
```

Concretely: if you add a new function to `src/api/users.py` that other
modules will use:
1. `modules/api.ctx.md` — update Public API table
2. `CROSS_INDEX.json` — if there are new `provides`
3. `python scripts/build_distilled.py`

**Rule of thumb:** `## Public API` and `## Invariants` must always be up to date.
`## Design Rationale` may go stale — it is historical.

### Trigger 2 — You Discover a New Invariant or One Breaks

This is the most important moment. Invariants in `.ctx.md` are the only way
future agents can learn from past mistakes.

```markdown
## Invariants  <!-- all-tiers -->

1. Change feature column names only via contract.yaml — never directly in code
   (Invariant 3 violated → 4h debugging, 2024-03-15)
2. New invariant: ...
```

After entering it: run `build_distilled.py` so the invariant lands in the
Haiku tier (the most important one for agents).

### Trigger 3 — Session End / Handoff to Another Agent

```bash
python scripts/new_knowledge.py "What the next agent should tackle"
```

This creates `.ctx/knowledge/LATEST.yaml`. What must go in there:

```yaml
milestone: "What is now true that was not true before"

cross_session_patterns:
  - discovery: "Non-obvious insight"
    applies_to: [module_a, module_b]
    # If two modules import each other -> deadlock. Always via bus.

next_session_hints:
  - priority: 1
    task: "What needs to be done next"
    context: ".ctx/.distilled/sonnet/relevant_module.ctx.md"

open_items:
  - item: "Deliberately deferred"
    why_deferred: "Concrete reason"
    trigger: "When to pick up again"
```

**What should NOT go in there:** Which files were changed (git log), how a
function works (read the code), what was done today (git blame).

---

## Building Cross-References — The Underestimated Feature

Cross-references in `.ctx.md` are not decoration. They are the only
way an agent knows **where to look next** without reading all files.

### Bad Cross-Reference (useless)

```markdown
## Cross-References
- infra/ — Infrastructure
- common/ — Utilities
```

### Good Cross-Reference (useful)

```markdown
## Cross-References  <!-- all-tiers -->

- [[modules/db.ctx|db]] — database connection that api/ uses for queries
- [[modules/auth.ctx|auth]] — JWT validation must run before every API handler
- [[modules/workers.ctx|workers]] — async jobs are dispatched via workers/, never directly
- [[architecture/API_CONTRACT.ctx|API_CONTRACT]] — why payload schema is only changeable via schema.py
```

**Rule:** Every cross-reference needs a "why" — otherwise it is useless.
An agent that knows "features depends on signals — because feature output goes over
the bus, not directly" can make correct decisions. One that only knows
"features depends on signals" cannot.

### Keeping CROSS_INDEX.json Correct

```bash
# Check whether CROSS_INDEX.json is complete
python -c "
import json
with open('.ctx/CROSS_INDEX.json') as f:
    ci = json.load(f)
modules = set(ci['modules'].keys())
for name, data in ci['modules'].items():
    for dep in data.get('depends_on', []):
        if dep not in modules:
            print(f'MISSING: {name}.depends_on contains {dep}, but {dep} has no module entry')
"
```

---

## Checklist: Full Operational Readiness

### Initial Setup Complete When:

```
[ ] .ctx/ is in the project root (not somewhere else)
[ ] INDEX.md shows real modules, no template placeholders
[ ] CROSS_INDEX.json has all packages with real depends_on/provides
[ ] Every package that agents will touch has a .ctx.md
[ ] Every .ctx.md has tier tags (<!-- all-tiers -->, <!-- sonnet+ -->, etc.)
[ ] Every .ctx.md has at minimum: Purpose, Public API, Invariants
[ ] build_distilled.py runs through without errors
[ ] Haiku distillates look sensible (not empty, not too large)
[ ] Dispatch rule is in CLAUDE.md / AGENTS.md of the project
[ ] A test dispatch to a module was done and the agent had the right context
```

### Ongoing Usage Healthy When:

```
[ ] build_distilled.py runs after every .ctx.md change
[ ] New invariants are entered into .ctx.md immediately (not "later")
[ ] Session end: knowledge/LATEST.yaml is up to date
[ ] Public API changes → .ctx.md Public API table updated immediately
[ ] CROSS_INDEX.json reflects real dependencies (no drift)
[ ] Distillates are never older than the source (check MANIFEST.json timestamp)
```

---

## Common Mistakes

### Mistake 1 — .ctx.md Without Tier Tags

```markdown
## Design Rationale
Why this design...
```

**Problem:** Section appears in all tiers. Haiku receives Design Rationale
it does not need and pays for it in tokens.

**Fix:** Always tag:
```markdown
## Design Rationale  <!-- opus-only -->
```

### Mistake 2 — Distillates Not Rebuilt After Changes

**Problem:** Agent reads `.ctx/.distilled/haiku/features.ctx.md` and sees
a month-old state. Works against outdated invariants.

**Fix:** `build_distilled.py` in a pre-commit hook or as a Makefile target.

```bash
# .git/hooks/pre-commit
#!/bin/bash
cd .ctx && python scripts/build_distilled.py --quiet
git add .ctx/.distilled/
```

### Mistake 3 — CROSS_INDEX.json Never Updated

**Problem:** A new package is added, never appears in CROSS_INDEX.json.
Agents don't know it exists or what it does.

**Fix:** CROSS_INDEX.json is part of the Definition of Done for every new package.

### Mistake 4 — knowledge/LATEST.yaml Stays Empty

**Problem:** Next session starts from scratch. All learnings, patterns,
open items are gone.

**Fix:** `new_knowledge.py` runs at the end of every significant session.

### Mistake 5 — Invariants in .ctx.md Go Stale

**Problem:** Code has changed, invariant no longer applies, but still
appears in the distillate. Agent follows a wrong invariant.

**Fix:** Invariants are the first thing checked during refactoring.
If an invariant breaks, it must be removed from .ctx.md immediately (or updated).

---

## Navigation

[[INDEX]] · [[OBSIDIAN]] · [[README]] · [[CLAUDE]] · [[AGENTS]] · [[modules/example.ctx|example module]] · [[architecture/example_pattern.ctx|example pattern]] · [[examples/openclaw/INDEX|OpenClaw example]]
