# Agent Dispatch Rules

> Copy the relevant section into your project's CLAUDE.md / AGENTS.md.

---

## Context Distillation (Required for ALL Agent Dispatches)

Before dispatching any sub-agent or starting any task:

1. Identify which modules the agent will work on
2. Include the right tier context in the prompt:
   - Haiku / fast workers:   "READ FIRST: .ctx/.distilled/haiku/{module}.ctx.md"
   - Sonnet / manager agents: "READ FIRST: .ctx/.distilled/sonnet/{module}.ctx.md"
   - Opus / architect tasks:  "READ FIRST: .ctx/modules/{module}.ctx.md"
3. For architecture tasks: also include .ctx/architecture/

No agent dispatch without matching .ctx context.

---

## Module Mapping

<!-- Fill with your actual modules -->

| Package / Folder | .ctx file |
|-----------------|-----------|
| src/example/    | modules/example.ctx.md |

---

## Exceptions (no .ctx needed)

- Pure config changes (JSON/YAML only)
- Documentation updates (.md files)
- Test-only changes that don't touch new APIs

---

## Navigation

[[INDEX]] · [[AGENTS]] · [[GUIDE]] · [[OBSIDIAN]] · [[modules/example.ctx|example module]] · [[examples/openclaw/INDEX|OpenClaw example]]
