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

## Purpose


<!-- One paragraph. What does this module do? Why does it exist? -->

The `example` module manages [describe domain here]. It provides:
- **ExampleService** (`service.py`): Business logic for [X]
- **ExampleRepository** (`repository.py`): Data access for [X]


## Public API


<!-- Only list what other modules actually call. Internal helpers go in medium+. -->

| Class / Function | Signature | Purpose |
|-----------------|-----------|---------|
| `ExampleService.create()` | `async (data: dict) -> Entity` | Create new entity |
| `ExampleService.get()` | `async (id: str) -> Entity \| None` | Fetch by ID |
| `ExampleRepository.save()` | `async (entity: Entity) -> None` | Persist to DB |


## Invariants


<!-- Hard rules. Every agent must know these. Repeat them even if they're in CROSS_INDEX.json. -->

1. All writes go through `ExampleService`, never direct repository calls from outside this module
2. Cache entries always have explicit TTL — never set without expiry
3. `ExampleRepository` is never imported outside `ExampleService`


## Cross-References


- Depends on: [database] — replace with your database technology
- Depends on: [cache] — replace with your cache technology
- Used by: [api] — REST endpoints call ExampleService
- Architecture: see architecture/DATA_FLOW.ctx.md for full request lifecycle
  <!-- ↑ Create architecture/DATA_FLOW.ctx.md using architecture/example_pattern.ctx.md as template -->
