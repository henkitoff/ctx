---
module: modules/example
type: codebase
depends_on: [database, cache]
depended_by: [api]
provides: [ExampleService, ExampleRepository]
invariants:
  - "All writes go through ExampleService, never direct DB calls"
  - "Cache TTL is always set explicitly, never implicit"
keywords: [example, service, repository, cache]
---

<!--
  HOW TO USE THIS FILE AS A TEMPLATE
  ===================================
  1. Rename to your module name (e.g. auth.ctx.md, billing.ctx.md)
  2. Update frontmatter (depends_on, provides, invariants, keywords)
  3. Fill each section — keep <!-- all-tiers --> sections SHORT (they cost tokens for every agent)
  4. Run scripts/build_distilled.py to regenerate .distilled/
  5. Update CROSS_INDEX.json to match your frontmatter
  6. Update INDEX.md Quick Navigation table
-->

## Purpose  <!-- all-tiers -->

<!-- One paragraph. What does this module do? Why does it exist? -->

The `example` module manages [describe domain here]. It provides:
- **ExampleService** (`service.py`): Business logic for [X]
- **ExampleRepository** (`repository.py`): Data access for [X]

## Public API  <!-- all-tiers -->

<!-- Only list what other modules actually call. Internal helpers go in sonnet+. -->

| Class / Function | Signature | Purpose |
|-----------------|-----------|---------|
| `ExampleService.create()` | `async (data: dict) -> Entity` | Create new entity |
| `ExampleService.get()` | `async (id: str) -> Entity \| None` | Fetch by ID |
| `ExampleRepository.save()` | `async (entity: Entity) -> None` | Persist to DB |

## Invariants  <!-- all-tiers -->

<!-- Hard rules. Every agent must know these. Repeat them even if they're in CROSS_INDEX.json. -->

1. All writes go through `ExampleService`, never direct repository calls from outside this module
2. Cache entries always have explicit TTL — never set without expiry
3. `ExampleRepository` is never imported outside `ExampleService`

## Key Patterns  <!-- sonnet+ -->

<!-- Patterns that inform HOW to extend this module correctly. -->

**Pattern: Service wraps repository**
```python
# Correct
service = ExampleService(repo=ExampleRepository(db))
entity = await service.create(data)

# Wrong — bypasses service-layer validation
entity = await repo.save(raw_data)
```

**Anti-pattern: Cache stampede**
Always use `get_or_set()` with a lock, never check-then-set without locking.

**Error handling:**
- `NotFoundError` → HTTP 404
- `ValidationError` → HTTP 422
- All other errors → HTTP 500, log with full context

## Internal Structure  <!-- sonnet+ -->

```
src/example/
├── service.py       ← Public interface (import this)
├── repository.py    ← DB access (only used by service.py)
├── models.py        ← Data models (ORM / schema)
├── cache.py         ← Cache helpers
└── errors.py        ← Module-specific exceptions
```

## Design Rationale  <!-- opus-only -->

<!-- Why was it built this way? What alternatives were considered? -->

**Why service + repository separation?**
Keeps business logic testable without a real database. The repository can be
mocked in unit tests; integration tests hit the real DB.

**Why explicit cache TTL?**
An early version used default TTL (infinite) which caused stale data incidents
after deployments. Now TTL is required at call site — compiler error if missing.

**Alternatives considered:**
- Active Record pattern: rejected because it couples models to DB queries,
  making testing harder
- CQRS: considered for write-heavy paths, deferred until needed

## Cross-References  <!-- all-tiers -->

- Depends on: [database] — replace with your database technology
- Depends on: [cache] — replace with your cache technology
- Used by: [api] — REST endpoints call ExampleService
- Architecture: see [[architecture/example_pattern.ctx|example_pattern]] for the architecture doc template
- Template guide: [[INDEX]] · [[GUIDE]]
