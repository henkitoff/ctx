---
module: architecture/<% tp.file.title %>
type: architecture
purpose: "[One line: what cross-cutting concern this pattern governs]"
affects: []

tags: [ctx/architecture]
aliases: []
---

<!--
  Architecture docs describe PATTERNS, not modules.
  Use this for: data flow, security model, error handling, auth, messaging, etc.
  Tier tags work the same as in module docs.
  When done: update CROSS_INDEX.json `global_invariants` and add to Canvas.
-->

## Overview  <!-- all-tiers -->

`<% tp.file.title %>` defines how [what cross-cutting concern] is handled across the system.
All modules that [do X] MUST follow this pattern.

## Rules  <!-- all-tiers -->

1. [Hard constraint — if violated, it is a bug]
2. [Hard constraint]
3. [Hard constraint]

## Flow  <!-- sonnet+ -->

```
[Entry Point]
     │
     ▼
[Step A] ────► [Step B]
     │               │
     ▼               ▼
[Result A]     [Result B]
```

## Implementation Guide  <!-- sonnet+ -->

How to apply this pattern in a new module:

```python
# Correct
class NewService:
    def correct_way(self):
        pass  # follows the pattern

# Wrong — violates rule N because [reason]
class BadService:
    def wrong_way(self):
        pass
```

## Anti-Patterns  <!-- sonnet+ -->

- **Never do [X]** — because [consequence]
- **Never do [Y]** — because [consequence]

## Rationale  <!-- opus-only -->

`<% tp.file.title %>` was introduced after [incident or problem that motivated it].

**Alternatives considered:**
- [Alternative A]: rejected because [reason]
- [Alternative B]: considered for [context], deferred until [condition]

## Affected Modules  <!-- all-tiers -->

All modules that [do X]. See `CROSS_INDEX.json` for the current list.

- [[modules/[module-a]|module-a]]
- [[modules/[module-b]|module-b]]

> **After saving this file:**
> 1. Add to `CROSS_INDEX.json` under `global_invariants` if this introduces hard constraints
> 2. Add an orange node to `architecture.canvas`
> 3. Run `python scripts/build_distilled.py` if you added tier-tagged sections
