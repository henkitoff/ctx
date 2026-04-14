---
module: architecture/plugin-system
type: architecture
purpose: Plugin boundary, manifest contract, adapter pattern, SDK surface
affects: [plugins, channels, gateway, extensions, packages/plugin-sdk]
---

## Overview  <!-- all-tiers -->

OpenClaw has 99 bundled plugins and supports third-party plugins. The plugin
system has a **hard architectural boundary**: extensions import only the public
SDK (`openclaw/plugin-sdk/*`), never internal `src/**` paths.

## The Plugin Boundary  <!-- all-tiers -->

```
┌─────────────────────────────────────────────────────────┐
│ extensions/*  (bundled plugins)                         │
│ third-party plugins                                     │
│                                                         │
│   import ONLY: openclaw/plugin-sdk/*                   │
│   import NEVER: ../src/**, ../../src/**                 │
└──────────────────────┬──────────────────────────────────┘
                       │ uses types from
                       ↓
┌─────────────────────────────────────────────────────────┐
│ packages/plugin-sdk  (public SDK package)               │
│   re-exports from src/plugin-sdk                        │
└──────────────────────┬──────────────────────────────────┘
                       │ implements contracts from
                       ↓
┌─────────────────────────────────────────────────────────┐
│ src/plugins/  (plugin system core)                      │
│   registry, manifest validation, runtime contracts      │
└─────────────────────────────────────────────────────────┘
```

**Enforcement:** `pnpm check-additional` (architecture gate) runs in CI.
Any `extensions/*` file importing from `src/**` is a build error.

## Plugin Manifest  <!-- all-tiers -->

Every plugin ships an `openclaw.plugin.json`:

```json
{
  "id": "telegram",
  "name": "Telegram",
  "version": "1.0.0",
  "kind": "channel",
  "config": {
    "schema": {
      "token": { "type": "string", "secret": true, "label": "Bot Token" }
    }
  },
  "capabilities": ["messaging", "groups", "files"],
  "auth": { "type": "token", "fields": ["token"] },
  "setup": { "interactive": true }
}
```

The manifest is the **source of truth** for:
- Plugin capabilities (what it can do)
- Config schema (what the user must provide)
- Auth requirements
- Setup wizard presence

Core code **never hardcodes plugin IDs** — it queries the registry by
capability or kind.

## Adapter Pattern  <!-- sonnet+ -->

Channel plugins implement adapters as needed (all optional except `config`):

```typescript
const telegramPlugin: ChannelPlugin = {
  id: "telegram",
  meta: { name: "Telegram", category: "messaging" },
  capabilities: { messaging: true, groups: true },

  config: { parse: TelegramConfigSchema.parse },

  outbound: {
    send: async ({ content }, ctx) => { /* send via Telegram Bot API */ },
    receiveHook: (app, ctx) => {
      app.post("/webhook/telegram/:token", async (req) => {
        await ctx.dispatch({ content: req.body.message.text, peer: req.body.message.from.id })
      })
    },
  },

  auth: {
    login: async (ctx) => { /* link bot token */ },
    logout: async (ctx) => { /* revoke */ },
  },

  status: {
    check: async (ctx) => ({ ok: true, detail: "Connected" }),
  },
}
```

## Plugin Loading Sequence  <!-- sonnet+ -->

```
Gateway/CLI startup
  → PluginRegistry loads all manifests from disk (no code import yet)
  → Registry validates manifest schema
  → Capabilities indexed for fast lookup

On first use (lazy):
  → Registry.getById("telegram") triggers code import
  → Plugin module instantiates adapters
  → Adapters bound to runtime context
  → Available for message dispatch
```

## Rules  <!-- all-tiers -->

1. Extensions import **only** `openclaw/plugin-sdk/*`
2. Manifest is source of truth for capabilities — no ambient registration
3. Plugin runtime is **lazy** — never eager-loaded on startup
4. Core queries registry by capability — never hardcodes plugin IDs
5. Plugin-managed state goes in plugin-owned storage — not in core config

## Affected Modules  <!-- all-tiers -->

- [[modules/plugins.ctx|plugins]] — registry, manifest validation, runtime contracts
- [[modules/channels.ctx|channels]] — channel plugins implement `ChannelPlugin` adapter
- [[modules/gateway.ctx|gateway]] — plugin HTTP routes dispatched from gateway
- [[modules/agents.ctx|agents]] — provider plugins supply LLM access to agents
- [[modules/hooks.ctx|hooks]] — hook plugins registered via manifest
