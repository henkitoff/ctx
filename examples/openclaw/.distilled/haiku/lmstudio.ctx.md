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
