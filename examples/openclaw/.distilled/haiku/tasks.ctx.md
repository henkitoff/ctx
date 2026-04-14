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


## Cross-References


- [[modules/agents.ctx|agents]] — `dispatchTask` creates isolated agent runs; `cron` + `gateway` tools used by agents
- [[modules/gateway.ctx|gateway]] — cron tick events fired by gateway; task status queryable via gateway RPC
- [[modules/hooks.ctx|hooks]] — hooks can trigger task dispatch on system events
- [[modules/config.ctx|config]] — cron schedules persisted via `mutateConfigFile()`
