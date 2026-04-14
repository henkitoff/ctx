---
module: modules/tasks
type: codebase
depends_on: [agents, config, gateway]
depended_by: [gateway, hooks]
provides: [TaskRunner, CronScheduler, dispatchTask, FlowEngine]
invariants:
  - "Cron jobs run in isolated agent contexts — they do not share state with interactive sessions"
  - "Task cancellation is best-effort — in-flight agent turns are not interrupted mid-token"
  - "Cron schedules are stored in config — not in process memory"
keywords: [tasks, cron, scheduler, background, flows, automation, periodic, jobs]

tags: [ctx/module]
---

## Purpose


The `tasks` module handles **background agent execution**: one-shot tasks, recurring
cron jobs, and multi-step flows. It lets agents (and operators) schedule work
outside the interactive session loop — from simple `"run every morning"` digests
to complex multi-agent pipelines.

Key components:
- **`TaskRunner`** — Execute agent turns in the background with audit trail
- **`CronScheduler`** — Cron-expression scheduling, enable/disable, run history
- **`FlowEngine`** — Multi-step agent pipelines (`tasks flow`)
- **`cron` / `gateway` agent tools** — In-session tools to create and manage jobs


## Public API


| Export | Type | Purpose |
|--------|------|---------|
| `dispatchTask` | fn | Queue a background agent task |
| `TaskRunner` | class | Execute tasks with audit, notify, cancel |
| `CronScheduler` | class | Add/edit/remove cron jobs; manage run history |
| `FlowEngine` | class | Multi-step flow execution |
| `listTasks` | fn | List running and recent background tasks |
| `cancelTask` | fn | Best-effort cancel of a queued/running task |


## Invariants


1. Cron jobs run in **isolated agent contexts** — no shared state with interactive sessions
2. Task cancellation is **best-effort** — in-flight agent turns finish their current LLM call
3. Cron schedules are **persisted in config** — survive gateway restarts
4. Flow steps are **sequential by default** — parallel branches require explicit branching config


## Key Patterns


**Cron job management (CLI):**
```bash

# Add a daily digest task

openclaw cron add "0 8 * * *" \
  --agent researcher \
  --message "Summarize top Hacker News stories and send to my Telegram"


# Inspect and manage

openclaw cron list              # all scheduled jobs
openclaw cron status            # next run times, last results
openclaw cron runs <job-id>     # run history for a job
openclaw cron enable/disable <job-id>
openclaw cron rm <job-id>
openclaw cron run <job-id>      # trigger manually now
```

**Agent creating its own cron job (via `cron` tool):**
```typescript
// Agent can schedule itself for recurring tasks
cron({
  schedule: "0 9 * * 1-5",   // weekdays at 9am
  agentId: "researcher",
  message: "Check for new papers on AI agents and summarize",
  sessionKey: "telegram/me",  // deliver to this channel
})
```

**Background task dispatch:**
```bash

# From CLI — run agent task in background

openclaw agent --agent writer \
  --message "Write a blog post about local LLMs" \
  --background


# Monitor background tasks

openclaw tasks list             # running + recent
openclaw tasks show <task-id>   # full output + status
openclaw tasks notify <task-id> # re-send completion notification
openclaw tasks cancel <task-id> # best-effort cancel
openclaw tasks audit            # usage + cost report
```

**Flow execution (multi-step pipelines):**
```bash

# Flows are named multi-step agent pipelines

openclaw tasks flow list        # list defined flows
openclaw tasks flow run <name>  # execute a flow
```


## Internal Structure


```
src/tasks/
├── task-runner/
│   ├── index.ts            ← dispatchTask, TaskRunner class
│   ├── audit.ts            ← Audit trail (cost, tokens, duration)
│   ├── notify.ts           ← Completion notification routing
│   └── cancel.ts           ← Best-effort cancellation
├── cron/
│   ├── scheduler.ts        ← CronScheduler — parse, store, fire
│   ├── persistence.ts      ← Persist schedules to config
│   ├── history.ts          ← Run history + result storage
│   └── tick.ts             ← Gateway cron tick event handler
├── flows/
│   ├── engine.ts           ← FlowEngine — step execution
│   ├── parser.ts           ← Flow definition parsing
│   └── steps/
│       ├── agent-step.ts   ← Agent turn step
│       └── condition.ts    ← Conditional branching
└── tools/
    ├── cron-tool.ts        ← `cron` agent tool implementation
    └── gateway-tool.ts     ← `gateway` agent tool implementation
```


## Design Rationale


**Why isolated contexts for cron jobs?**
Cron jobs may run hours after the triggering session ends. Sharing state with an
interactive session would require holding memory across restarts and create subtle
race conditions. Isolation makes cron semantics predictable: each run starts fresh,
with only the scheduled message and agent config as inputs.

**Why best-effort cancellation?**
LLM calls cannot be interrupted mid-generation without losing the streaming token
buffer. The cancel flag is checked between tool calls and before the next LLM
invocation. This is consistent with how most agent frameworks handle cancellation —
`abort` at the token level would require provider-side support that not all LLM
providers implement.

**Why cron schedules in config (not DB)?**
OpenClaw is designed to run without a database dependency. Config-file persistence
keeps the deployment simple (no migration, no schema versioning) and makes cron
schedules auditable via git. The tradeoff is that concurrent edits to the config
are handled by `mutateConfigFile()` (atomic write) not by database transactions.


## Cross-References


- [[modules/agents.ctx|agents]] — `dispatchTask` creates isolated agent runs; `cron` + `gateway` tools used by agents
- [[modules/gateway.ctx|gateway]] — cron tick events fired by gateway; task status queryable via gateway RPC
- [[modules/hooks.ctx|hooks]] — hooks can trigger task dispatch on system events
- [[modules/config.ctx|config]] — cron schedules persisted via `mutateConfigFile()`
