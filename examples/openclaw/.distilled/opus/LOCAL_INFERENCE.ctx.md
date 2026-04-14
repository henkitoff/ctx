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


## Provider Routing Flow


```
User sends message
       │
       ▼
agents/agent-command.ts
  resolveDefaultModelForAgent()
       │
       ├─ "lmstudio:meta-llama/Llama-3.2-3B"  ──► LmStudioProvider
       │      │ checkLmStudioHealth()
       │      ├─ ok  ──► POST /v1/chat/completions (stream)
       │      └─ fail ──► { available: false }
       │                        │
       │                        ▼  (cascade to next level)
       └─ "anthropic:claude-haiku-3-5" ──► AnthropicProvider
              │ cloud API call
              └─ streaming response
```

**Model ref → provider resolution:**
```typescript
// normalizeModelRef parses the scheme to select the provider plugin
const ref = normalizeModelRef("lmstudio:meta-llama/Llama-3.2-3B-Instruct")
// → scheme: "lmstudio" → PluginRegistry.getByScheme("lmstudio") → LmStudioProvider
```


## Config: Mixing Local and Cloud


```json
// ~/.openclaw/config.json
{
  "defaults": {
    "model": "lmstudio:meta-llama/Llama-3.2-3B-Instruct",
    "fallbackModel": "anthropic:claude-haiku-3-5"
  },
  "agents": {
    "research": {
      "model": "lmstudio:bartowski/Mistral-7B-Instruct",
      "fallbackModel": "openai:gpt-4o-mini"
    }
  },
  "plugins": {
    "lmstudio": {
      "baseUrl": "http://localhost:1234",
      "timeoutMs": 60000
    }
  }
}
```

The 4-level cascade (`session override → agent config → global default → FALLBACK_MODEL`)
is evaluated before any provider is contacted. Local providers are transparent to
the cascade — they just resolve to a provider plugin via their scheme prefix.


## Health Check Protocol


Every local provider implements a `checkHealth()` call before the session's first
inference call. Result is cached for the session lifetime:

```typescript
interface LocalProviderHealth {
  ok: boolean
  models: string[]         // available / loaded model names
  reason?: string          // human-readable failure reason
}

// For LM Studio:
GET http://localhost:1234/v1/models
→ 200 OK → { ok: true, models: ["meta-llama/Llama-3.2-3B-Instruct"] }
→ ECONNREFUSED → { ok: false, reason: "LM Studio server not running" }
```

**Timing:** health check must complete in < 500ms. If it times out, treat as
`{ ok: false }`. Cloud providers skip health checks (they are always assumed
reachable; their errors are handled inline).


## Anti-Patterns


- **Never inline health check per-request** — adds 100ms+ latency to every token; check once per session and cache
- **Never use bare model names** — `"Llama-3.2-3B"` is ambiguous; always `"lmstudio:publisher/model"`
- **Never assume a model is loaded** — LM Studio auto-loads on first request, but VRAM limits may prevent it; health check returns loaded models
- **Never import provider plugins across the plugin boundary** — `agents/` must access providers only via `PluginRegistry`, never by direct import


## LM Studio — Endpoint Reference


| Endpoint | Method | Used for |
|----------|--------|---------|
| `/v1/models` | GET | Health check, enumerate loaded models |
| `/v1/chat/completions` | POST | Chat inference (streaming via SSE) |
| `/v1/embeddings` | POST | Embedding generation (for memory plugins) |

Default base URL: `http://localhost:1234`. Configurable per-plugin in `config.json`.
Optional API token: stored in secrets as `SecretRef`, sent as `Authorization: Bearer <token>`.


## Rationale


**Why a scheme prefix in model refs instead of a provider field?**
Considered: `{ model: "meta-llama/Llama-3.2-3B", provider: "lmstudio" }`.
Rejected because: the provider field duplicates information, requires both fields
to be kept in sync, and breaks the 4-level cascade which passes a single model
ref string through all levels. The URI scheme (`lmstudio:`) encodes provider
selection in a single atomic string — the cascade can pass it unchanged and
`normalizeModelRef` resolves provider from it at dispatch time.

**Why health check per-session rather than per-request?**
Per-request health checks double the latency of every inference call (an extra
round-trip before each POST). Per-session caching means one extra 50ms call at
session start, invisible in the overall session duration. The cached result is
valid for the session lifetime — if LM Studio crashes mid-session, the next
`POST /v1/chat/completions` will fail naturally and return an error to the agent.

**Why support both OpenAI-compatible API and lmstudio-js SDK?**
The OpenAI-compatible `/v1/` API is sufficient for inference. The native `lmstudio-js`
SDK adds model management (load/unload, VRAM stats) but couples to LM Studio
specifically. The plugin defaults to the OpenAI API for broad compatibility;
VRAM management via native SDK is an opt-in capability for operators running
resource-constrained hardware (e.g. shared developer machines, edge devices).


## Affected Modules


- [[modules/lmstudio.ctx|lmstudio]] — reference implementation of this pattern
- [[modules/agents.ctx|agents]] — `resolveDefaultModelForAgent`, `normalizeModelRef`
- [[modules/plugins.ctx|plugins]] — `PluginRegistry.getByScheme()`, `ProviderPlugin` contract
- [[modules/config.ctx|config]] — `defaults.model`, `fallbackModel`, `plugins.lmstudio.*`
- [[modules/infra.ctx|infra]] — fetch wrapper used by all provider HTTP calls
