---
module: architecture/LOCAL_INFERENCE
type: architecture
purpose: Provider routing pattern — local LLM inference vs cloud APIs, health checks, fallback cascade
affects: [agents, plugins, config, lmstudio, infra]

tags: [ctx/architecture]
---

## Overview


`LOCAL_INFERENCE` defines how OpenClaw routes LLM requests to **local inference
servers** (LM Studio, Ollama, llama.cpp) alongside cloud providers (Anthropic,
OpenAI). The same 4-level model selection cascade in `agents/` applies — the
provider plugin is resolved from the model ref scheme (`lmstudio:`, `anthropic:`,
`openai:`, …). Local providers must pass a health check before dispatch;
if unavailable, the cascade falls through to the next configured level.


## Rules


1. Local providers run `checkHealth()` before the **first** inference call per session — never inline before each call
2. A failed health check returns `{ available: false }` — agents cascade to the next model level automatically
3. Model refs carry an explicit scheme prefix (`lmstudio:publisher/model`) — bare model names are rejected by `normalizeModelRef`
4. All provider HTTP calls use `infra`'s fetch wrapper — never raw `fetch`
5. Provider plugins import only `openclaw/plugin-sdk/*` — they never access `src/**`


## Affected Modules


- [[modules/lmstudio.ctx|lmstudio]] — reference implementation of this pattern
- [[modules/agents.ctx|agents]] — `resolveDefaultModelForAgent`, `normalizeModelRef`
- [[modules/plugins.ctx|plugins]] — `PluginRegistry.getByScheme()`, `ProviderPlugin` contract
- [[modules/config.ctx|config]] — `defaults.model`, `fallbackModel`, `plugins.lmstudio.*`
- [[modules/infra.ctx|infra]] — fetch wrapper used by all provider HTTP calls
