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


## Rules


1. Model cascade must complete before any prompt is sent to the LLM
2. Skill snapshot is **loaded once** — never during tool execution
3. Tool execution is **synchronous** within the agent loop
4. ACP is the **only** channel for agent ↔ gateway communication


## Affected Modules


`config` → `agents` → `acp` → (Pi agent-core) → `gateway/protocol`
