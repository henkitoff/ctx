---
module: modules/plugins
type: codebase
depends_on: [config, infra]
depended_by: [agents, channels, gateway, hooks, commands]
provides: [PluginRegistry, PluginManifest, ChannelPlugin, ProviderPlugin, resolvePluginAuth]
invariants:
  - "Plugin capabilities declared in manifest — no ambient registration"
  - "Plugin runtime is lazy — instantiated on first use, not on startup"
  - "Core never hardcodes bundled plugin IDs — use manifest metadata"
keywords: [plugins, registry, manifest, channel, provider, hooks, runtime, extensions]
---

## Purpose


The `plugins` module is the **plugin system core**: discovery, loading, manifest
validation, runtime contracts, and hook dispatch. It mediates between the 99
bundled extensions and the OpenClaw core.

Key components:
- **`registry.ts`** — Plugin catalog and loading
- **`manifest-types.ts`** — Plugin metadata schema (`openclaw.plugin.json`)
- **`types.ts`** — Plugin capability contracts (Channel, Provider, Memory, Task…)
- **`runtime/`** — Plugin runtime execution and auth setup
- **`contracts/`** — Plugin enforcement and validation
- **`hook-types.ts`** — Hook registration and dispatch


## Public API


| Export | Type | Purpose |
|--------|------|---------|
| `PluginRegistry` | class | Load, lookup, and iterate plugins |
| `PluginManifest` | type | Plugin `openclaw.plugin.json` schema |
| `ChannelPlugin` | type | Full channel plugin contract |
| `ProviderPlugin` | type | LLM/tool provider plugin contract |
| `resolvePluginAuth` | fn | Resolve auth credentials for a plugin |
| `resolveSyntheticAuth` | fn | Synthesize auth from config for legacy plugins |
| `PluginRuntime` | type | Runtime API surface exposed to plugins |


## Invariants


1. Plugin capabilities are **declared in manifest** — core never infers them
2. Plugin runtime is **lazy** — import and instantiate on first use, not startup
3. Core never hardcodes plugin IDs — query via `registry.getById()` or capability
4. Extensions (in `extensions/`) import **only** `openclaw/plugin-sdk/*`


## Plugin Kinds


| Kind | What it provides |
|------|-----------------|
| `channel` | Messaging integration (Discord, Telegram, WhatsApp, …) |
| `provider` | LLM or tool integration (Anthropic, OpenAI, LM Studio, …) |
| `media` | Image/video/audio generation or understanding |
| `memory` | Embedding store and retrieval |
| `task` | Workflow / task runner integration |
| `hook` | Respond to system events (message received, cron tick, …) |


## Cross-References


- `extensions/` — 99 bundled plugins consuming `openclaw/plugin-sdk/*`
- `packages/plugin-sdk/` — Public SDK package
- [[modules/channels.ctx|channels]] — Channel plugin type + adapter contracts
- [[modules/hooks.ctx|hooks]] — Hook dispatch system
- [[modules/lmstudio.ctx|lmstudio]] — example `provider` plugin implementation
- Architecture: see [[architecture/PLUGIN_SYSTEM.ctx|PLUGIN_SYSTEM]] for full design
- Architecture: see [[architecture/LOCAL_INFERENCE.ctx|LOCAL_INFERENCE]] for provider-kind routing pattern
