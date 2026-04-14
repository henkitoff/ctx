# Obsidian Setup — Humans and Agents, One Vault

This `.ctx` repo is designed so the **same files serve two audiences equally**:

- **Humans** navigate via Obsidian's Graph View, backlinks, Canvas, Dataview tables
- **Agents** navigate via `INDEX.md`, `CROSS_INDEX.json`, `LATEST.yaml`, and distilled tier files

No duplication. No "docs for humans, separate context for agents." One source of truth.

---

## How it works: the dual-audience contract

| Feature | Human experience | Agent experience |
|---------|-----------------|-----------------|
| YAML frontmatter | Obsidian Properties panel | Machine-readable metadata |
| `INDEX.md` | Opening note / home | Mandatory first read |
| `CROSS_INDEX.json` | — (humans use Canvas) | Dependency graph, no parsing needed |
| `modules/*.ctx.md` | Rich markdown with properties | Module doc with tier-tagged sections |
| Tier tags `<!-- all-tiers -->` | Invisible in rendered view | Controls what distilled tiers include |
| `.distilled/haiku/` | — (humans read master files) | Token-efficient context for fast models |
| `knowledge/LATEST.yaml` | Living project status note | Session handoff, read at start of every session |
| Canvas `.canvas` | Visual architecture overview | — (agents use CROSS_INDEX.json) |
| Dataview queries | Auto-generated module tables | — |

---

## 1. Vault setup

### Option A — `.ctx/` inside an existing project vault (recommended)

Your project already has an Obsidian vault at the repo root. Add `.ctx/` as a subfolder:

```
my-project/          ← Obsidian vault root
├── .obsidian/
├── .ctx/            ← This repo, cloned as a subfolder
│   ├── INDEX.md
│   ├── modules/
│   ├── architecture/
│   ├── knowledge/
│   └── scripts/
├── src/
├── docs/
└── README.md
```

In Obsidian → Settings → Files & Links: set **Default location for new notes** to your `docs/` folder, not `.ctx/` (keep `.ctx/` structured, not a dumping ground).

### Option B — `.ctx/` IS the vault

Clone this repo directly and open it as a vault in Obsidian. Works for pure knowledge bases, documentation projects, or when you want `.ctx/` to be the primary workspace.

```
ctx/                 ← Obsidian vault root (this repo)
├── .obsidian/       ← Created by Obsidian
├── INDEX.md
├── modules/
├── architecture/
├── knowledge/
└── scripts/
```

---

## 2. Plugins to install

Open Obsidian → Settings → Community Plugins → Browse

| Plugin | Why | Required? |
|--------|-----|-----------|
| **Dataview** | Auto-generated module tables from frontmatter | Recommended |
| **Templater** | Consistent new module creation | Recommended |
| **Kanban** | Track open_items from knowledge distillates | Optional |
| **Git** | Commit knowledge distillates from inside Obsidian | Optional |

---

## 3. Frontmatter as Obsidian Properties

Every `.ctx.md` file has YAML frontmatter that Obsidian renders as **Properties**
(the metadata panel at the top of each note in reading/live preview mode).

Add `tags` and `aliases` to get the most from Obsidian's graph and search:

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

# Obsidian-specific additions (no effect on agents):
tags: [ctx/module, ctx/codebase]
aliases: [AuthService, auth-module]
---
```

**Tag convention:**
- `ctx/module` — all module docs
- `ctx/architecture` — all architecture docs
- `ctx/knowledge` — all knowledge distillates
- `ctx/example` — example/template files (filter these OUT of production queries)

These tags power Graph View filtering and Dataview queries.

---

## 4. Graph View — see your dependency graph visually

Settings → Graph View → Filters:

**Show only module docs:**
```
tag:#ctx/module OR tag:#ctx/architecture
```

**Color groups (Settings → Graph View → Groups):**
- `tag:#ctx/module` → Blue
- `tag:#ctx/architecture` → Orange
- `tag:#ctx/knowledge` → Green

**Enable:** Files → turn off `Attachments`, turn off `Orphans` (distilled files have no backlinks — that's fine)

**Pro tip:** Add `[[wikilinks]]` inside your `.ctx.md` files to generate edges in the graph:

```markdown
## Cross-References  <!-- all-tiers -->

- Depends on: [[modules/database.ctx|database]]
- Depends on: [[modules/cache.ctx|cache]]
- Used by: [[modules/api.ctx|api]]
```

Obsidian renders these as clickable links AND shows them as graph edges. Agents can follow them as relative file paths (strip the `[[` / `]]` syntax). The graph now mirrors `CROSS_INDEX.json` visually without any extra tooling.

---

## 5. Dataview — live module tables

Install Dataview plugin, then paste these queries into any note (e.g., into `INDEX.md` directly):

### All modules with dependencies

````markdown
```dataview
TABLE
  provides AS "Exports",
  depends_on AS "Depends on",
  depended_by AS "Used by"
FROM "modules"
WHERE type = "codebase" AND !contains(tags, "ctx/example")
SORT module ASC
```
````

### Modules by keyword (search)

````markdown
```dataview
LIST
FROM "modules"
WHERE contains(keywords, "auth") OR contains(keywords, "security")
```
````

### Architecture docs overview

````markdown
```dataview
TABLE purpose AS "Covers", affects AS "Modules affected"
FROM "architecture"
WHERE type = "architecture"
SORT file.name ASC
```
````

### Recent knowledge distillates

````markdown
```dataview
TABLE topic AS "Topic", milestone AS "Milestone"
FROM "knowledge"
WHERE date != null
SORT date DESC
LIMIT 5
```
````

These tables update automatically when you add or edit module files. No manual index maintenance.

---

## 6. Templater — create new modules consistently

Install Templater, then configure:

Settings → Templater → **Template folder location**: `obsidian/templates`

Now when you create a new note inside `modules/`, it auto-applies the module template.

Settings → Templater → **Folder templates**:
- `modules/` → `obsidian/templates/new-module.md`
- `architecture/` → `obsidian/templates/new-architecture.md`
- `knowledge/` → `obsidian/templates/new-knowledge.md`

The template files live in `obsidian/templates/` — see that folder in this repo.

**After filling in the template**, run the build script to generate tier distillates:
```bash
python scripts/build_distilled.py
# or for a named example project:
python scripts/build_distilled.py --project myproject
```

---

## 7. Canvas — architecture as a living diagram

Create `architecture.canvas` at the vault root (or in `obsidian/`).

**Build it from `CROSS_INDEX.json`:**
1. One node per module → link each node to its `modules/X.ctx.md` file
2. One node per service (Redis, Postgres, S3…)
3. Draw arrows for `depends_on` relationships
4. Color code: modules blue, services grey, architecture docs orange

**In Obsidian Canvas:**
- Double-click empty space → Add note → link to existing file
- Draw edges by dragging from a node's edge handle
- Add groups (e.g., "Core", "Infrastructure", "External")

The Canvas is the **human view**. `CROSS_INDEX.json` is the **agent view**. They represent the same information — keep them in sync when you add modules.

**Sync rule:** Whenever you add a module to `CROSS_INDEX.json`, add a node to the Canvas. Takes 30 seconds and keeps both audiences in sync.

---

## 8. Knowledge distillates as living notes

`knowledge/LATEST.yaml` is both:
- A YAML file agents parse at session start
- An Obsidian note that shows current project state in the Properties panel

To get the most from Obsidian with knowledge distillates:

**Add tags to LATEST.yaml:**
```yaml
tags: [ctx/knowledge, ctx/latest]
date: "2026-04-14"
topic: "Auth module refactor"
milestone: "All 47 tests green"
```

**Pin LATEST.yaml as your vault home:**
Settings → Core Plugins → **Starred** → Star `knowledge/LATEST.yaml`

Now every time you open Obsidian, your first view is the current project state — same as every agent's first read.

**Kanban board from open_items:**
If you install the Kanban plugin, create `obsidian/kanban.md`:

````markdown
---
kanban-plugin: basic
---

## Backlog

- [ ] [[knowledge/LATEST.yaml|Open item 1]]

## In Progress

## Done
````

Manually sync `open_items` from LATEST.yaml to Kanban when starting a session. Takes 2 minutes and gives you a visual task board that both you and agents understand.

---

## 9. Tier tags — invisible to you, essential for agents

Tier tags (`<!-- all-tiers -->`, `<!-- sonnet+ -->`, `<!-- opus-only -->`) are HTML comments. Obsidian **does not render HTML comments** — they are completely invisible in reading mode and live preview.

This is intentional:
- **Humans** read the full master file — all sections visible
- **Agents** read the tier-appropriate distilled file — only relevant sections

You never have to think about tier tags while reading in Obsidian. You only interact with them when **writing** a new section:

```markdown
## New Section  <!-- sonnet+ -->

This section will only appear in .distilled/sonnet/ and .distilled/opus/,
not in .distilled/haiku/. Write it in source mode.
```

**To see tier tags while writing:** switch to Source Mode (Ctrl/Cmd+E) or use the inline title bar toggle.

---

## 10. Agent dispatch from inside Obsidian

Add this block to your `INDEX.md` (agents read it on every session start):

```markdown
## Agent Dispatch Rule

Before starting any task, load the right tier context:

| Model size | Load this file |
|-----------|---------------|
| Haiku / fast workers | .distilled/haiku/{module}.ctx.md |
| Sonnet / manager agents | .distilled/sonnet/{module}.ctx.md |
| Opus / architect tasks | modules/{module}.ctx.md |

For architecture tasks: also load architecture/{PATTERN}.ctx.md
```

This block renders as a normal table in Obsidian and is machine-readable by agents. One source, two audiences.

---

## 11. Daily workflow

### As a human

| When | What to do |
|------|-----------|
| Start of day | Open `knowledge/LATEST.yaml` → check `next_session_hints` |
| Add new module | Cmd+N → Obsidian auto-applies module template → fill in → run `build_distilled.py` |
| End of session | Run `python scripts/new_knowledge.py "topic"` → fill in `cross_session_patterns` |
| Architecture change | Update Canvas + `CROSS_INDEX.json` (30 sec each) |

### As / with an agent

| When | What the agent reads |
|------|---------------------|
| Session start | `INDEX.md` → `knowledge/LATEST.yaml` → `next_session_hints` |
| Any module task | `.distilled/{tier}/{module}.ctx.md` (injected by dispatch rule) |
| Architecture task | `architecture/{PATTERN}.ctx.md` + `CROSS_INDEX.json` |
| End of session | Writes to `knowledge/LATEST.yaml` (or you fill it in manually) |

---

## 12. Quick start checklist

**One-time setup (15 min):**
- [ ] Open this repo as an Obsidian vault (or add `.ctx/` to your existing vault)
- [ ] Install: Dataview + Templater
- [ ] Set Templater folder templates: `modules/` → `obsidian/templates/new-module.md`
- [ ] Add `tags: [ctx/module]` to existing module `.ctx.md` frontmatter
- [ ] Configure Graph View color groups (`tag:#ctx/module` → blue, etc.)
- [ ] Star `knowledge/LATEST.yaml` as vault home note
- [ ] Copy the Dataview queries from Section 5 into your `INDEX.md`

**Per-project setup (30 min):**
- [ ] Create one `modules/X.ctx.md` per domain (copy from `modules/example.ctx.md`)
- [ ] Fill `CROSS_INDEX.json` with real dependencies
- [ ] Run `python scripts/build_distilled.py` → generates all distilled tiers
- [ ] Create `architecture.canvas` with one node per module
- [ ] Add dispatch rule to your `CLAUDE.md` / `AGENTS.md`
- [ ] Run `python scripts/new_knowledge.py "Initial setup"` → fill in first distillate

---

## 13. What does NOT go in `.ctx/` (Obsidian edition)

A common mistake: using Obsidian's free-form linking to pull arbitrary notes into `.ctx/`.

| Do not put in `.ctx/` | Put it here instead |
|----------------------|-------------------|
| Meeting notes, daily notes | `docs/journal/` or Obsidian's daily notes folder |
| Draft specs / half-baked ideas | `docs/specs/` |
| Personal annotations on code | Code comments in the actual source |
| Screenshots, diagrams | `docs/assets/` (link from `.ctx.md` if needed) |
| Link to external docs | Reference in Cross-References section only |

**The test:** Would an agent reading this file get confused by it? If yes, it doesn't belong in `.ctx/`.

---

## Navigation

[[INDEX]] · [[GUIDE]] · [[README]] · [[CLAUDE]] · [[AGENTS]] · [[modules/example.ctx|example module]] · [[examples/openclaw/INDEX|OpenClaw example]]
