---
module: architecture/AGENT_RUNTIME
type: architecture
purpose: Agent runtime internals — workspace, bootstrap files, agent loop, skills, compaction, hook points, queue modes
affects: [agents, sessions, tasks, hooks, memory, plugins]

tags: [ctx/architecture]
---

## Overview


OpenClaw runs a **single embedded agent runtime** per Gateway (built on Pi agent
core). Every session flows through the same pipeline: workspace preparation →
bootstrap file injection → skills loading → system prompt assembly → model
inference → tool execution → streaming reply → session persistence.

This doc covers the runtime internals: workspace layout, bootstrap files, agent
loop stages, hook intercept points, compaction, queue modes, and streaming.


## Workspace Layout


Default workspace: `~/.openclaw/workspace`. All file tools use this as cwd.
Not a hard sandbox — absolute paths can reach outside unless sandboxing is enabled.

```
~/.openclaw/workspace/
├── AGENTS.md          ← Operating instructions + memory rules (loaded every session)
├── SOUL.md            ← Persona, tone, boundaries (loaded every session)
├── USER.md            ← User profile and preferred address (loaded every session)
├── IDENTITY.md        ← Agent name, vibe, emoji (created during bootstrap ritual)
├── TOOLS.md           ← Local tool conventions (does NOT control tool availability)
├── HEARTBEAT.md       ← Short periodic task checklist (for heartbeat runs)
├── BOOT.md            ← Startup checklist on gateway restart (optional)
├── BOOTSTRAP.md       ← One-time first-run ritual (deleted after completion)
├── MEMORY.md          ← Long-term durable memory (loaded every DM session)
├── memory/
│   └── YYYY-MM-DD.md  ← Daily memory log (today + yesterday loaded automatically)
├── DREAMS.md          ← Dreaming sweep summaries + grounded backfill (optional)
├── skills/            ← Workspace-level skills (highest precedence)
└── canvas/            ← Canvas UI files for node displays
```

**Bootstrap file rules:**
- Blank files are skipped. Large files are truncated with a marker (`bootstrapMaxChars: 20000`, `bootstrapTotalMaxChars: 150000`).
- `BOOTSTRAP.md` is only created for a brand-new workspace; delete after the ritual.
- Disable bootstrap creation: `{ agent: { skipBootstrap: true } }`
- `openclaw setup` recreates missing defaults without overwriting existing files.


## Agent Loop Stages


```
agentCommand(sessionKey, message)
  │
  ├─ 1. Session resolution (sessionKey → sessionId → transcript)
  ├─ 2. Workspace preparation (sandbox redirect if enabled)
  ├─ 3. Skills snapshot (load once per session, reuse for all turns)
  ├─ 4. Bootstrap context injection (AGENTS.md, SOUL.md, USER.md, …)
  ├─ 5. System prompt assembly
  │       ├─ Base prompt (config or default)
  │       ├─ Provider contributions (model-specific headers)
  │       ├─ Skills listing (XML, ~97 chars + content per skill)
  │       └─ Tools listing
  ├─ 6. Pi agent run (runEmbeddedPiAgent)
  │       ├─ Serialized per session key + optional global queue
  │       ├─ Model auth resolution + thinking/verbose/trace defaults
  │       ├─ Event bridge: pi events → OpenClaw agent/tool/lifecycle streams
  │       └─ Timeout enforcement (agents.defaults.timeoutSeconds, default 48h)
  └─ 7. Reply assembly + delivery
          ├─ Block streaming: completed blocks emitted as they finish
          ├─ NO_REPLY token → suppress delivery silently
          └─ Duplicate messaging-tool sends removed from final payload
```


## Skills System


Skills are `SKILL.md` files teaching agents how to use tools. Loaded by precedence:

1. `<workspace>/skills` (highest — workspace-specific)
2. `<workspace>/.agents/skills` (project agent skills)
3. `~/.agents/skills` (personal agent skills)
4. `~/.openclaw/skills` (managed/local)
5. Bundled (shipped with install)
6. `skills.load.extraDirs` (lowest)

Skills are **snapshotted at session start** and reused for all turns. Changes
take effect on next new session (or via watcher hot-reload).

**ClawHub:** public skills registry at https://clawhub.ai
```bash
openclaw skills install <skill-slug>   # into workspace/skills/
openclaw skills update --all
```

**Gating (load-time):** `metadata.openclaw.requires.bins/env/config` filters skills
by binary presence, env vars, and config flags. Skills for missing binaries are excluded.

**Token cost:** 195 chars base + (97 + name + description + location) per skill.


## Affected Modules


- [[modules/agents.ctx|agents]] — agent command, model selection, tool execution, skills snapshot
- [[modules/sessions.ctx|sessions]] — session key derivation, transcript persistence
- [[modules/hooks.ctx|hooks]] — gateway hooks + plugin hook registration
- [[modules/memory.ctx|memory]] — memory files in workspace, memory flush
- [[modules/tasks.ctx|tasks]] — cron runs, background tasks, queue modes
- [[modules/plugins.ctx|plugins]] — plugin hooks, compaction providers
- [[architecture/MULTI_AGENT.ctx|MULTI_AGENT]] — multi-agent routing, sub-agents
