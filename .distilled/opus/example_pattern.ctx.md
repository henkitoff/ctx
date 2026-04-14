---
module: architecture/example-pattern
type: architecture
purpose: Template for architecture pattern documents
affects: [all modules]
---


<!--
  HOW TO USE THIS FILE AS A TEMPLATE
  ===================================
  Rename to the pattern name (e.g. DATA_FLOW.ctx.md, SECURITY_MODEL.ctx.md).
  Architecture docs use the same tier tags as module docs.
  Keep <!-- all-tiers --> short — agents pay per token.
-->


## Overview


<!-- One paragraph: what pattern is this, why does it exist? -->

[Pattern name] defines how [what cross-cutting concern] is handled across the system.
All modules that [do X] MUST follow this pattern.


## Rules


<!-- Hard constraints. If a module violates these, it's a bug. -->

1. [Rule 1 — short, unambiguous]
2. [Rule 2]
3. [Rule 3]


## Flow Diagram


<!-- ASCII diagram of the pattern in action -->

```
[Client]
   │
   ▼
[Module A] ──── calls ────► [Module B]
   │                            │
   ▼                            ▼
[Service X]              [Repository Y]
```


## Implementation Guide


<!-- How to implement this pattern in a new module. Code example. -->

```python

# Correct implementation

class NewService:
    def __init__(self, repo: NewRepository):
        self._repo = repo  # injected, not imported directly

    async def do_thing(self, data: dict) -> Entity:
        # validate first
        validated = self._validate(data)
        # then persist
        return await self._repo.save(validated)
```


## Anti-Patterns


<!-- What to avoid. Make it concrete. -->

- **Never do X** — because [consequence]
- **Never do Y** — because [consequence]


## Rationale


<!-- Why this pattern was chosen. What was rejected and why. -->

[Pattern name] was introduced after [incident / problem].
Alternatives considered:
- [Alternative A]: rejected because [reason]
- [Alternative B]: deferred to [condition]


## Affected Modules


All modules that [do X]. See CROSS_INDEX.json for the current list.
