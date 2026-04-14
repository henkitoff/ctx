🇬🇧 English · [🇩🇪 Deutsch](AGENTS.de.md)

# Agent Entry Point (Codex / GitHub Copilot)

Start here. Read INDEX.md first, then follow the task table.

## Dispatch Rules

- Always load the tier-appropriate distilled context before working
- Never skip .ctx context for non-trivial changes
- Check CROSS_INDEX.json for dependency impact before modifying a module

## Tier Selection

- Haiku / fast workers   → .distilled/haiku/{module}.ctx.md
- Sonnet / manager agents → .distilled/sonnet/{module}.ctx.md
- Opus / architect tasks  → modules/{module}.ctx.md

## Critical Invariants

See [[INDEX]] → Critical Invariants section.

---

## Navigation

[[INDEX]] · [[CLAUDE]] · [[GUIDE]] · [[OBSIDIAN]] · [[modules/example.ctx|example module]] · [[examples/openclaw/INDEX|OpenClaw example]]
