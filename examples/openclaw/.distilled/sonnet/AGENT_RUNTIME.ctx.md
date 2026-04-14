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


## Queue Modes


Controls how inbound messages behave while an agent turn is running:

| Mode | Behavior |
|------|----------|
| `steer` | Inject message after current tool calls, before next LLM call |
| `followup` | Hold until current turn ends, start new turn with queued payloads |
| `collect` | Like followup, but debounced — waits to collect multiple messages |

Configure per channel or globally. Steering is injected at the **next model boundary**,
not mid-tool-call.


## Compaction


When a session approaches the model's context window, older turns are summarized
into a persisted `compaction` entry and the conversation continues.

**Auto-compaction triggers:**
1. Overflow recovery — model returns context overflow error → compact → retry
2. Threshold maintenance — `contextTokens > contextWindow - reserveTokens` after a successful turn

**Pre-compaction memory flush (default: on):**
Before compacting, OpenClaw runs a silent `NO_REPLY` turn to write durable facts
to `memory/YYYY-MM-DD.md`. Config: `agents.defaults.compaction.memoryFlush`.

**Compaction settings:**
```json5
{
  agents: {
    defaults: {
      compaction: {
        model: "openrouter/anthropic/claude-sonnet-4-6",  // optional different model
        reserveTokens: 16384,
        keepRecentTokens: 20000,
        identifierPolicy: "strict",   // strict | off | custom
        notifyUser: false,
        memoryFlush: { enabled: true, softThresholdTokens: 4000 }
      }
    }
  }
}
```

**Manual compaction:** `/compact [instructions]` — guide the summary.
**vs Pruning:** pruning trims tool results in-memory without persisting; compaction summarizes and saves.


## Hook Points


Two hook systems intercept the agent lifecycle:


## Streaming


```json5
{
  agents: {
    defaults: {
      blockStreamingDefault: "off",            // enable per-channel with *.blockStreaming: true
      blockStreamingBreak: "text_end",         // text_end | message_end
      blockStreamingChunk: { min: 800, max: 1200 },   // soft chunking size
      blockStreamingCoalesce: true,            // merge idle chunks before send
    }
  }
}
```

- Block streaming emits completed assistant blocks as they finish (for long-form responses)
- Reasoning/thinking can be emitted as separate stream or as block replies
- `NO_REPLY` / `no_reply` as exact reply token → suppress delivery entirely


## Model Ref Format


```
"provider/model-id"

Examples:
  "anthropic/claude-opus-4-6"
  "openai/gpt-4o"
  "openrouter/moonshotai/kimi-k2"     ← provider prefix required for multi-slash IDs
  "lmstudio:meta-llama/Llama-3.2-3B"  ← scheme:publisher/model for local providers
  "ollama/llama3.1:8b"
```

Parsed by splitting on the **first** `/`. If provider is omitted, OpenClaw tries
aliases, then configured-provider match, then falls back to default provider.
Stale removed-provider defaults fall back to first configured provider/model.


## Sandboxing


Tool execution (exec, read, write, edit, apply_patch, process) can be isolated
in Docker or SSH backends. Gateway stays on host; only tools run sandboxed.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",           // off | all | cron | non-main
        scope: "agent",        // agent | shared
        backend: "docker",     // docker | ssh | openShell
        docker: {
          setupCommand: "apt-get update && apt-get install -y git",  // runs once on container create
        },
        workspaceRoot: "~/.openclaw/sandboxes",
        workspaceAccess: "rw",  // rw | ro | none
      }
    }
  }
}
```

**Browser sandboxing:** `sandbox.browser` isolates browser on a dedicated Docker network.
**Sandbox vs tool policy vs elevated:** separate controls — sandbox restricts filesystem/process access; tool policy controls which tools exist; elevated mode grants higher privileges for specific senders.


## Affected Modules


- [[modules/agents.ctx|agents]] — agent command, model selection, tool execution, skills snapshot
- [[modules/sessions.ctx|sessions]] — session key derivation, transcript persistence
- [[modules/hooks.ctx|hooks]] — gateway hooks + plugin hook registration
- [[modules/memory.ctx|memory]] — memory files in workspace, memory flush
- [[modules/tasks.ctx|tasks]] — cron runs, background tasks, queue modes
- [[modules/plugins.ctx|plugins]] — plugin hooks, compaction providers
- [[architecture/MULTI_AGENT.ctx|MULTI_AGENT]] — multi-agent routing, sub-agents
