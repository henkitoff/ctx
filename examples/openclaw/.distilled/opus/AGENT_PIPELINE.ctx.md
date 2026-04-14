---
module: architecture/agent-pipeline
type: architecture
purpose: Model selection cascade, skill loading, ACP protocol, tool execution loop
affects: [agents, acp, plugins, config, sessions]
---

## Overview


The agent pipeline runs inside `src/agents/agent-command.ts`. It resolves
which model to use, loads skills, assembles the system prompt, and runs the
Pi agent loop via the Agent Client Protocol (ACP).


## Pipeline Stages


```
agentCommand(sessionKey, message, config)
  │
  ├─ 1. Model Selection (4-level cascade)
  ├─ 2. Skill Snapshot (workspace discovery)
  ├─ 3. System Prompt Assembly
  ├─ 4. Pi Agent Spawn (via ACP)
  └─ 5. Tool Execution Loop (streaming)
```


## Model Selection Cascade


```typescript
// Resolved in order — first defined wins:
1. config.session?.overrides[sessionKey]?.model   // per-session user choice
2. config.agents?.[agentId]?.model                // per-agent config
3. config.defaults?.model                         // global default
4. FALLBACK_MODEL                                 // hardcoded last resort
```

Provider is resolved similarly. On rate-limit or error, the cascade tries the
next level automatically.


## Skill Snapshot


Skills are markdown files in `~/.openclaw/skills/` (or workspace). They are:
1. Discovered by `buildWorkspaceSkillSnapshot()` at session start
2. Filtered by agent config (`matchesSkillFilter`)
3. Injected into the system prompt as a "skills listing"
4. **Not reloaded mid-conversation** — snapshot is fixed for the session

```typescript
const snapshot = await buildWorkspaceSkillSnapshot(agentId, config)
// snapshot = [{ name: "research", content: "..." }, ...]
```


## System Prompt Assembly


Built from multiple contributions in order:
1. **Base prompt** — from `config.agents[agentId].systemPrompt` or default
2. **Provider contributions** — provider plugin can add model-specific headers
3. **Skills listing** — names + descriptions of available skills
4. **Tools listing** — built-in tools available to the agent


## ACP Communication


```
agents/pi-embedded-runner
  ↓ spawns Pi agent-core
  ↓ opens ACP channel

Pi agent-core
  ↓ ACP events (blocks, tool calls, end)

acp/server.ts
  ↓ event-mapper: Pi events → OpenClaw ChatEvent
  ↓ gateway RPC
  ↓ WebSocket
Client (CLI/App)
```


## Tool Execution Loop


```
Agent produces tool call:
  { type: "tool_use", name: "browser", input: { url: "..." } }
  ↓
Tool registry lookup: src/agents/tools/browser.ts
  ↓
Tool executes (blocking)
  ↓
Result injected back as tool_result message
  ↓
Agent continues
```

Built-in tools: `browser`, `canvas`, `cron`, `sessions`, `memory`


## Rules


1. Model cascade must complete before any prompt is sent to the LLM
2. Skill snapshot is **loaded once** — never during tool execution
3. Tool execution is **synchronous** within the agent loop
4. ACP is the **only** channel for agent ↔ gateway communication


## Affected Modules


`config` → `agents` → `acp` → (Pi agent-core) → `gateway/protocol`
