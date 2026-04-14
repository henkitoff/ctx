---
module: modules/hooks
type: codebase
depends_on: [plugins, config]
depended_by: [gateway, auto-reply]
provides: [HookEntry, dispatchHook, bundledHooks]
invariants:
  - "Hook dispatch is fire-and-forget — failures are logged, not propagated"
  - "before_tool_call: { block: true } is terminal — stops all lower-priority handlers"
  - "message_sending: { cancel: true } is terminal — { cancel: false } does NOT clear a prior cancel"
  - "Workspace hooks can add new hook names but cannot override bundled/managed/plugin hooks"
keywords: [hooks, events, webhooks, lifecycle, dispatch, automation, plugin-hooks, before_tool_call, session_memory]

tags: [ctx/module]
---

## Purpose


The `hooks` module is OpenClaw's **event dispatch system**. Two complementary systems:

1. **Internal hooks** — small TypeScript scripts discovered from directories, triggered by agent lifecycle events (`/new`, `/reset`, `/stop`, compaction, gateway startup, message flow)
2. **Plugin hooks** — 15+ hooks registered by plugins via the Plugin SDK; run inside the agent loop for deep integration (model override, prompt mutation, tool interception, message control)

| Export | Type | Purpose |
|--------|------|---------|
| `HookEntry` | type | Single hook config (trigger + handler) |
| `dispatchHook` | fn | Fire all hooks matching a trigger |
| `bundledHooks` | const | Built-in hook definitions |


## Invariants


1. **Fire-and-forget** — hook failures are logged, not re-thrown; other handlers continue
2. **Terminal guards:** `before_tool_call: { block: true }` stops all lower-priority handlers; `{ block: false }` is a no-op, does NOT clear a prior block
3. **Cancel semantics:** `message_sending: { cancel: true }` is terminal; `{ cancel: false }` does NOT clear a prior cancel
4. **Workspace hooks** cannot override bundled, managed, or plugin hooks with the same name
5. **Hook eligibility** checked via `metadata.openclaw.requires` (bins, env, config, OS) — ineligible hooks are skipped silently


## Internal Hook Events


| Event | When it fires |
|-------|--------------|
| `command:new` | `/new` command issued |
| `command:reset` | `/reset` command issued |
| `command:stop` | `/stop` command issued |
| `command` | Any command event (general listener) |
| `agent:bootstrap` | Before workspace bootstrap files are injected |
| `session:compact:before` | Before compaction summarizes history |
| `session:compact:after` | After compaction completes |
| `session:patch` | When session properties are modified (privileged clients only) |
| `gateway:startup` | After channels start and hooks are loaded |
| `message:received` | Inbound message from any channel |
| `message:transcribed` | After audio transcription completes |
| `message:preprocessed` | After all media and link understanding completes |
| `message:sent` | Outbound message delivered |


## Plugin Hooks (Agent Loop)


These run inside the agent loop or gateway pipeline, registered via Plugin SDK:

| Hook | Phase | What it does |
|------|-------|-------------|
| `before_model_resolve` | Pre-session (no messages) | Override provider/model deterministically |
| `before_prompt_build` | After session load (with messages) | Inject `prependContext`, `systemPrompt`, `prependSystemContext`, `appendSystemContext` |
| `before_agent_reply` | After inline actions, before LLM call | Claim the turn — return synthetic reply or silence turn entirely |
| `agent_end` | After completion | Inspect final message list + run metadata |
| `before_compaction` | Before compaction | Observe or annotate compaction cycle |
| `after_compaction` | After compaction | Post-compaction inspection |
| `before_tool_call` | Before tool execution | Intercept/modify tool params; `{ block: true }` is terminal |
| `after_tool_call` | After tool execution | Inspect/modify tool results |
| `tool_result_persist` | Synchronously, before transcript write | Transform tool results before persistence |
| `before_install` | Before skill/plugin install scan | Block or approve installs; `{ block: true }` is terminal |
| `message_received` | Inbound message | Pre-process inbound message |
| `message_sending` | Before outbound send | Cancel or modify; `{ cancel: true }` is terminal |
| `message_sent` | After outbound delivery | Post-delivery inspection |
| `session_start` | Session lifecycle start | Setup, logging, initialization |
| `session_end` | Session lifecycle end | Cleanup, persistence, reporting |
| `gateway_start` | Gateway startup | Initialize global state |
| `gateway_stop` | Gateway shutdown | Cleanup connections, flush state |

**`before_prompt_build` injection fields:**
- `prependContext` — per-turn dynamic text prepended to conversation
- `systemPrompt` — replace system prompt entirely
- `prependSystemContext` / `appendSystemContext` — inject into system prompt space (stable, cached)


## Cross-References


- [[modules/plugins.ctx|plugins]] — plugins register plugin hooks via Plugin SDK
- [[modules/agents.ctx|agents]] — plugin hooks fire inside the agent loop (before/after_tool_call, before_prompt_build, etc.)
- [[modules/gateway.ctx|gateway]] — gateway hooks (gateway_start/stop, message_received/sending/sent)
- [[modules/tasks.ctx|tasks]] — automation layer built on top of hooks
- [[architecture/AGENT_RUNTIME.ctx|AGENT_RUNTIME]] — hook intercept points in the agent loop
