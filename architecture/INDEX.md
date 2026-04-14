# Architecture Index

Cross-cutting patterns that span multiple modules.
These documents explain HOW the system works, not what each module does.

## Documents

| File | What it covers |
|------|---------------|
| example_pattern.ctx.md | Annotated template for architecture docs |
| DATA_FLOW.ctx.md | ← Create this: end-to-end request lifecycle |
| SECURITY_MODEL.ctx.md | ← Create this: auth, secrets, permissions |
| ERROR_HANDLING.ctx.md | ← Create this: error taxonomy + HTTP mapping |

## When to add an architecture doc

Add one when a pattern **spans 3+ modules** and would otherwise be
re-explained in each module's `.ctx.md`. Put the pattern here once,
cross-reference it from the modules.

---

## Navigation

[[INDEX]] · [[architecture/example_pattern.ctx|example pattern template]] · [[GUIDE]]
