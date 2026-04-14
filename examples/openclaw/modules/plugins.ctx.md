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

## Purpose  <!-- all-tiers -->

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

## Public API  <!-- all-tiers -->

| Export | Type | Purpose |
|--------|------|---------|
| `PluginRegistry` | class | Load, lookup, and iterate plugins |
| `PluginManifest` | type | Plugin `openclaw.plugin.json` schema |
| `ChannelPlugin` | type | Full channel plugin contract |
| `ProviderPlugin` | type | LLM/tool provider plugin contract |
| `resolvePluginAuth` | fn | Resolve auth credentials for a plugin |
| `resolveSyntheticAuth` | fn | Synthesize auth from config for legacy plugins |
| `PluginRuntime` | type | Runtime API surface exposed to plugins |

## Invariants  <!-- all-tiers -->

1. Plugin capabilities are **declared in manifest** — core never infers them
2. Plugin runtime is **lazy** — import and instantiate on first use, not startup
3. Core never hardcodes plugin IDs — query via `registry.getById()` or capability
4. Extensions (in `extensions/`) import **only** `openclaw/plugin-sdk/*`

## Plugin Kinds  <!-- all-tiers -->

| Kind | What it provides |
|------|-----------------|
| `channel` | Messaging integration (Discord, Telegram, WhatsApp, …) |
| `provider` | LLM or tool integration (Anthropic, OpenAI, LM Studio, …) |
| `media` | Image/video/audio generation or understanding |
| `memory` | Embedding store and retrieval |
| `task` | Workflow / task runner integration |
| `hook` | Respond to system events (message received, cron tick, …) |

## Key Patterns  <!-- sonnet+ -->

**Plugin manifest (`openclaw.plugin.json`):**
```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "description": "Adds a custom tool to OpenClaw",
  "configSchema": {
    "type": "object",
    "additionalProperties": false
  }
}
```

**Entry point:**
```typescript
// index.ts
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { Type } from "@sinclair/typebox";

export default definePluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  description: "Adds a custom tool to OpenClaw",
  register(api) {
    // Required tool — always available
    api.registerTool({
      name: "my_tool",
      description: "Do a thing",
      parameters: Type.Object({ input: Type.String() }),
      async execute(_id, params) {
        return { content: [{ type: "text", text: `Got: ${params.input}` }] };
      },
    });

    // Optional tool — user must opt in via tools.allow
    api.registerTool({ name: "workflow_tool", ... }, { optional: true });
  },
});
```

Channel plugins use `defineChannelPluginEntry` instead. Provider plugins: see `modules/lmstudio.ctx.md` for a complete example.

**Plugin capabilities (registration methods):**

| Capability | Method |
|------------|--------|
| Text inference (LLM) | `api.registerProvider(...)` |
| Channel / messaging | `api.registerChannel(...)` |
| Speech (TTS/STT) | `api.registerSpeechProvider(...)` |
| Realtime transcription | `api.registerRealtimeTranscriptionProvider(...)` |
| Realtime voice | `api.registerRealtimeVoiceProvider(...)` |
| Media understanding | `api.registerMediaUnderstandingProvider(...)` |
| Image / video / music generation | `api.registerImageGenerationProvider(...)` etc. |
| Web fetch / search | `api.registerWebFetchProvider(...)` / `registerWebSearchProvider(...)` |
| Agent tools | `api.registerTool(...)` |
| Event hooks | `api.registerHook(...)` |
| HTTP routes | `api.registerHttpRoute(...)` |
| CLI subcommands | `api.registerCli(...)` |
| Custom commands | `api.registerCommand(...)` |
| Compaction providers | `api.registerCompactionProvider(...)` |

**Import convention (always use focused subpaths):**
```typescript
// Correct
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";

// Wrong — monolithic root is deprecated
import { ... } from "openclaw/plugin-sdk";
```

**Hook guard semantics:**
- `before_tool_call: { block: true }` — terminal, stops lower-priority handlers
- `before_tool_call: { block: false }` — no-op (does NOT clear a prior block)
- `before_tool_call: { requireApproval: true }` — pauses execution, prompts user
- `message_sending: { cancel: true }` — terminal, stops lower-priority handlers
- `before_install: { block: true }` — terminal, blocks skill/plugin install

**Publishing:**
```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
openclaw plugins install clawhub:@myorg/openclaw-my-plugin
# Or from npm (ClawHub checked first)
openclaw plugins install @myorg/openclaw-my-plugin
```

## Internal Structure  <!-- sonnet+ -->

```
src/plugins/
├── registry.ts             ← Plugin loading + lookup
├── manifest-types.ts       ← openclaw.plugin.json schema
├── types.ts                ← All capability contracts (2 000+ lines)
├── hook-types.ts           ← Hook registration + dispatch
├── runtime/
│   ├── index.ts            ← RuntimeLogger, RuntimeContext
│   └── auth.ts             ← Auth resolution
├── contracts/
│   └── validation.ts       ← Capability enforcement
└── memory-state.ts         ← Memory plugin capability
```

## Design Rationale  <!-- opus-only -->

Lazy plugin loading was chosen because the majority of plugins are unused in
any given session (99 bundled, but a user might only use 2-3 channels). Eager
loading would waste startup time and memory.

The manifest-as-source-of-truth pattern ensures plugins can be introspected
without importing their code — important for the doctor, setup wizard, and
config UI which need to render plugin metadata without executing plugin code.

## Cross-References  <!-- all-tiers -->

- `extensions/` — 99 bundled plugins consuming `openclaw/plugin-sdk/*`
- `packages/plugin-sdk/` — Public SDK package
- [[modules/channels.ctx|channels]] — Channel plugin type + adapter contracts
- [[modules/hooks.ctx|hooks]] — Hook dispatch system
- [[modules/lmstudio.ctx|lmstudio]] — example `provider` plugin implementation
- Architecture: see [[architecture/PLUGIN_SYSTEM.ctx|PLUGIN_SYSTEM]] for full design
- Architecture: see [[architecture/LOCAL_INFERENCE.ctx|LOCAL_INFERENCE]] for provider-kind routing pattern
