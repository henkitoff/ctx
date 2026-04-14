---
module: modules/agents
type: codebase
depends_on: [plugins, config, acp, channels, gateway, sessions]
depended_by: [commands, gateway]
provides: [agentCommand, AgentHarness, resolveDefaultModelForAgent, buildWorkspaceSkillSnapshot]
invariants:
  - "Agents never call channel adapters directly — route via gateway/auto-reply"
  - "Model selection follows: session override → agent config → global default → fallback"
  - "Skills snapshot is loaded once per session, not per token"
  - "Model ref format: provider/model-id — first slash splits provider from model"
  - "Auth profile pinned per session for cache warmth — rotates only on reset/compaction/cooldown"
keywords: [agent, model, tools, skills, harness, acp, pi-agent, thinking, failover, model-ref, bootstrap]
---

## Purpose


The `agents` module is the **agent execution runtime**: it orchestrates model
selection, skill loading, system prompt assembly, tool dispatch, and Pi agent
spawning via the Agent Client Protocol (ACP).

Key components:
- **`agent-command.ts`** — Main orchestration entry point
- **`model-catalog.ts`** — Model registry, selection, fallback
- **`harness/`** — Execution wrapper types
- **`tools/`** — Built-in tools (browser, canvas, cron, sessions, …)
- **`skills/`** — Workspace skill discovery and loading
- **`auth-profiles/`** — Auth provider credential resolution
- **`pi-embedded-runner/`** — Pi agent-core integration
- **`system-prompt.ts`** — System prompt assembly


## Public API


| Export | Type | Purpose |
|--------|------|---------|
| `agentCommand` | fn | Main entry: execute agent for a session |
| `AgentHarness` | type | Harness carrying session + model context |
| `AnyAgentTool` | type | Union of all built-in tool types |
| `resolveDefaultModelForAgent` | fn | Model selection with fallback |
| `normalizeModelRef` | fn | Normalize model string to canonical form |
| `buildWorkspaceSkillSnapshot` | fn | Discover + load skills for current session |


## Invariants


1. Agents **never** call channel adapters directly — delivery goes via `auto-reply/`
2. Model selection order: session override → agent config → global default → fallback
3. Skill snapshot is loaded **once per session invocation**, not per token/tool
4. Tool execution is synchronous within the agent loop — no concurrent tool calls


## Cross-References


- [[modules/acp.ctx|acp]] — agent spawning protocol
- [[modules/plugins.ctx|plugins]] — skill loading, provider resolution via `PluginRegistry`
- [[modules/config.ctx|config]] — model catalog, auth profiles
- [[modules/channels.ctx|channels]] — chat context (session, transcript)
- [[modules/sessions.ctx|sessions]] — session key, transcript, compaction
- [[modules/hooks.ctx|hooks]] — plugin hooks fire inside agent loop (before_tool_call, before_prompt_build, etc.)
- [[modules/lmstudio.ctx|lmstudio]] — local LLM provider; `normalizeModelRef` routes `lmstudio:` refs here
- [[modules/memory.ctx|memory]] — workspace bootstrap files, pre-compaction memory flush
- Architecture: see [[architecture/AGENT_RUNTIME.ctx|AGENT_RUNTIME]] for workspace layout + 7-stage agent loop
- Architecture: see [[architecture/AGENT_PIPELINE.ctx|AGENT_PIPELINE]] for full pipeline flow
- Architecture: see [[architecture/LOCAL_INFERENCE.ctx|LOCAL_INFERENCE]] for provider routing + fallback cascade
- Architecture: see [[architecture/MULTI_AGENT.ctx|MULTI_AGENT]] for multi-agent routing and sub-agents
