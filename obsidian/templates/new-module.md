---
module: modules/<% tp.file.title %>
type: codebase
depends_on: []
depended_by: []
provides: []
invariants:
  - ""
keywords: [<% tp.file.title %>]

tags: [ctx/module]
aliases: []
---

<!--
  Templater filled in the module name from your note title.
  Fill in the frontmatter, then work through each section.
  When done: run scripts/build_distilled.py and update CROSS_INDEX.json.
-->

## Purpose  <!-- all-tiers -->

The `<% tp.file.title %>` module manages [describe domain here]. It provides:
- **[MainClass]** (`[file].py`): [what it does]

## Public API  <!-- all-tiers -->

| Class / Function | Signature | Purpose |
|-----------------|-----------|---------|
| `[Class.method()]` | `async ([args]) -> [Return]` | [one-line] |

## Invariants  <!-- all-tiers -->

1. [Hard rule — every agent must know this]
2. [Hard rule]

## Key Patterns  <!-- sonnet+ -->

**Pattern: [name]**
```
# Correct
[example]

# Wrong — [why it breaks]
[counter-example]
```

**Error handling:**
- `[ErrorType]` → [how caller handles it]

## Internal Structure  <!-- sonnet+ -->

```
src/<% tp.file.title %>/
├── [main_file].py    ← Public interface (import this)
├── [impl_file].py    ← Internal implementation
└── [models].py       ← Data models / schemas
```

## Design Rationale  <!-- opus-only -->

**Why [key decision]?**
[Explain the trade-off. What was rejected and why.]

**Alternatives considered:**
- [Alternative A]: rejected because [reason]
- [Alternative B]: deferred until [condition]

## Cross-References  <!-- all-tiers -->

- Depends on: [[modules/[dep]|[dep]]]
- Used by: [[modules/[consumer]|[consumer]]]
- Architecture: see [[architecture/[PATTERN]|[PATTERN]]] for cross-cutting rules

> **After saving this file:**
> 1. Run `python scripts/build_distilled.py` to regenerate `.distilled/`
> 2. Add to `CROSS_INDEX.json` (copy depends_on / depended_by from frontmatter)
> 3. Add a row to `INDEX.md` Quick Navigation table
> 4. Add a node to `architecture.canvas`
