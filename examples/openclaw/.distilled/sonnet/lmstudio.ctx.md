---
module: modules/lmstudio
type: codebase
depends_on: [plugins, config, infra, secrets]
depended_by: [agents]
provides: [LmStudioProvider, LmStudioConfig, checkLmStudioHealth, LmStudioModelRef]
invariants:
  - "All LM Studio API calls go through infra's fetch wrapper — never raw fetch or axios"
  - "Health check (GET /v1/models) runs before the first inference call each session"
  - "Model refs use lmstudio:publisher/model-name format — never bare model names"
  - "Extension imports only openclaw/plugin-sdk/* — never src/**"
keywords: [lmstudio, local-llm, inference, provider, openai-compatible, embeddings, privacy]

tags: [ctx/module]
---

## Purpose


The `lmstudio` extension is a **provider plugin** that routes LLM inference to a
locally running [LM Studio](https://lmstudio.ai) server instead of a cloud API.
LM Studio exposes an OpenAI-compatible REST API at `http://localhost:1234/v1/`
— this plugin wraps that endpoint and integrates it into OpenClaw's model
selection and provider resolution pipeline.

Key components:
- **`lmstudio-provider.ts`** — `ProviderPlugin` implementation (chat completions, streaming)
- **`health.ts`** — `checkLmStudioHealth()` via `GET /v1/models`
- **`model-ref.ts`** — Model ref parsing / normalization (`lmstudio:publisher/model`)
- **`embeddings.ts`** — Optional embedding support for memory plugins
- **`openclaw.plugin.json`** — Plugin manifest declaring `provider` capability


## Public API


| Export | Type | Purpose |
|--------|------|---------|
| `LmStudioProvider` | class | `ProviderPlugin` implementation — registered via manifest |
| `checkLmStudioHealth` | fn | `GET /v1/models` → `{ ok: boolean, models: string[] }` |
| `LmStudioModelRef` | type | Branded string `lmstudio:publisher/model-name` |
| `LmStudioConfig` | type | Plugin config schema (`baseUrl`, `apiToken?`, `timeoutMs`) |
| `parseLmStudioRef` | fn | Parse `lmstudio:X/Y` → `{ publisher, model }` |


## Invariants


1. All HTTP calls use `infra`'s fetch wrapper — never raw `fetch` or `axios`
2. `checkLmStudioHealth()` runs once before the first inference call per session; result is cached
3. Model refs always carry the `lmstudio:` prefix — `normalizeModelRef` (agents) enforces this
4. If the health check fails, the provider returns `{ available: false }` — agents fall back via cascade
5. Plugin imports only `openclaw/plugin-sdk/*` — never `src/**`


## Key Patterns


**Plugin manifest (`extensions/lmstudio/openclaw.plugin.json`):**
```json
{
  "id": "lmstudio",
  "name": "LM Studio",
  "version": "1.0.0",
  "kind": "provider",
  "config": {
    "schema": {
      "baseUrl": { "type": "string", "default": "http://localhost:1234" },
      "apiToken": { "type": "string", "secret": true, "required": false },
      "timeoutMs": { "type": "number", "default": 60000 }
    }
  },
  "capabilities": ["chat-completions", "embeddings"],
  "auth": { "type": "token", "fields": ["apiToken"], "optional": true }
}
```

**Chat completion call:**
```typescript
// extensions/lmstudio/src/lmstudio-provider.ts
// Imports ONLY from openclaw/plugin-sdk — never from src/**
import type { ProviderPlugin, ChatCompletionRequest } from "openclaw/plugin-sdk"

export class LmStudioProvider implements ProviderPlugin {
  async chatCompletion(req: ChatCompletionRequest) {
    const resp = await this.fetch(`${this.baseUrl}/v1/chat/completions`, {
      method: "POST",
      body: JSON.stringify({
        model: parseLmStudioRef(req.modelRef).model,
        messages: req.messages,
        stream: true,
        temperature: req.temperature ?? 0.7,
      }),
    })
    return streamOpenAiResponse(resp)  // SSE → AsyncIterable<ChatEvent>
  }
}
```

**Health check + graceful degradation:**
```typescript
import { checkLmStudioHealth } from "./health"

const health = await checkLmStudioHealth(config.baseUrl)
if (!health.ok) {
  // Provider signals unavailability — agent cascade tries next level
  return { available: false, reason: "LM Studio server not reachable" }
}
// health.models = ["meta-llama/Llama-3.2-3B-Instruct", ...]
```

**Model ref normalization (in `agents/model-catalog.ts`):**
```typescript
// config.json:
// "defaults": { "model": "lmstudio:meta-llama/Llama-3.2-3B-Instruct" }
const ref = normalizeModelRef("lmstudio:meta-llama/Llama-3.2-3B-Instruct")
// → { scheme: "lmstudio", publisher: "meta-llama", model: "Llama-3.2-3B-Instruct" }
// → routes to LmStudioProvider
```


## Internal Structure


```
extensions/lmstudio/
├── openclaw.plugin.json     ← Plugin manifest
├── package.json             ← Declares "openclaw/plugin-sdk" as peer dep
└── src/
    ├── index.ts             ← Plugin entry point, exports LmStudioProvider
    ├── lmstudio-provider.ts ← ProviderPlugin implementation
    ├── health.ts            ← checkLmStudioHealth() — GET /v1/models
    ├── model-ref.ts         ← parseLmStudioRef(), LmStudioModelRef type
    ├── embeddings.ts        ← POST /v1/embeddings (memory plugin interop)
    └── stream.ts            ← SSE → AsyncIterable<ChatEvent> adapter
```

**LM Studio server endpoints used:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/models` | GET | Health check, enumerate loaded models |
| `/v1/chat/completions` | POST | Streaming inference (SSE) |
| `/v1/embeddings` | POST | Embedding generation (memory plugins) |


## Cross-References


**openclaw internals:**
- [[modules/plugins.ctx|plugins]] — `ProviderPlugin` contract this extension implements
- [[modules/agents.ctx|agents]] — `normalizeModelRef` routes `lmstudio:` refs here
- [[modules/infra.ctx|infra]] — fetch wrapper used for all HTTP calls
- [[modules/secrets.ctx|secrets]] — optional API token stored as `SecretRef`
- [[modules/config.ctx|config]] — `baseUrl`, `timeoutMs` read from plugin config block
- Architecture: [[architecture/LOCAL_INFERENCE.ctx|LOCAL_INFERENCE]] — provider routing pattern

**LM Studio API reference (external lib):**
- [[lmstudio/INDEX|LM Studio — Full Docs Index]]
- [[lmstudio/overview.ctx|overview]] — auth, TTL, headless deployment, server setup
- [[lmstudio/openai-compat.ctx|openai-compat]] — `/v1/chat/completions` used for inference here
- [[lmstudio/rest-api.ctx|rest-api]] — `/api/v1/models` used for health check
- [[lmstudio/typescript.ctx|typescript]] — `@lmstudio/sdk` for native model management (optional enhancement)
