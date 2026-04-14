---
module: modules/config
type: codebase
depends_on: [secrets, infra]
depended_by: [agents, gateway, plugins, channels, cli]
provides: [loadConfig, writeConfigFile, mutateConfigFile, OpenClawConfig]
invariants:
  - "Config mutations are always atomic via mutateConfigFile() — never write directly"
  - "Secret values stored as SecretRef { $ref } — never plain strings"
  - "Legacy config keys migrated in doctor --fix, not silently in load"
keywords: [config, configuration, schema, mutation, secrets, sessions, validation]
---

## Purpose


The `config` module manages the **complete configuration lifecycle**: loading
from disk, validating with Zod, atomic mutations, session state, and secret
reference resolution.

Config lives at `~/.openclaw/config.json` (JSON5 format).

Key components:
- **`config.ts`** — Main loader and in-memory cache
- **`types.ts`** — `OpenClawConfig` schema
- **`validation.ts`** — Zod validation
- **`io.ts`** — File read/write with locking
- **`mutate.ts`** — Atomic read-modify-write
- **`sessions/`** — Per-session state (transcript, overrides)
- **`secrets.ts`** — `SecretRef` resolution


## Public API


| Export | Type | Purpose |
|--------|------|---------|
| `loadConfig` | fn | Load + validate config from disk |
| `writeConfigFile` | fn | Write config (low-level, prefer `mutate`) |
| `mutateConfigFile` | fn | Atomic read-modify-write config |
| `OpenClawConfig` | type | Full config schema |
| `ModelProviderConfig` | type | Per-provider model config |
| `deriveSessionKey` | fn | Derive session key from channel + peer |
| `resolveSessionKey` | fn | Resolve session key to agent assignment |


## Invariants


1. **Always use `mutateConfigFile()`** for writes — never write file directly
2. Secrets are stored as `SecretRef` (`{ $ref: "provider/key" }`) in config
3. Legacy config keys are **not silently migrated** on load — use `doctor --fix`
4. Config cache is invalidated on file change (watch-based)


## Config Schema (simplified)


```typescript
type OpenClawConfig = {
  gateway?: {
    mode: "local" | "remote"
    port?: number
    auth?: { type: "token"; token: SecretRef }
    tls?: { cert: string; key: string }
  }
  agents?: {
    [agentId: string]: {
      model?: string
      provider?: string
      authProfile?: string
      systemPrompt?: string
    }
  }
  channels?: {
    [channelId: string]: {
      enabled: boolean
      config: Record<string, unknown>   // channel-specific, validated by channel plugin
    }
  }
  plugins?: {
    entries: { [pluginId: string]: PluginConfig }
  }
  hooks?: {
    internal: { entries: HookEntry[] }
  }
  defaults?: {
    model?: string
    provider?: string
  }
  session?: {
    defaults: SessionDefaults
    overrides: Record<SessionKey, SessionOverrides>
  }
}
```


## Key Patterns


**Atomic mutation:**
```typescript
// CORRECT — atomic read-modify-write
await mutateConfigFile(configPath, (config) => {
  config.channels ??= {}
  config.channels["discord"] = { enabled: true, config: { token: secretRef } }
  return config
})

// WRONG — race condition, partial write risk
const config = await loadConfig(configPath)
config.channels["discord"] = { ... }
await writeConfigFile(configPath, config)
```

**Secret reference:**
```typescript
// In config (stored on disk)
{ "token": { "$ref": "discord/bot-token" } }

// At runtime, resolved via secrets module
const token = await resolveSecretValue(config.channels.discord.config.token)
// → "Bot xxxxxxxxxxx"
```


## Design Rationale


Atomic mutations via `mutateConfigFile` prevent partial writes under concurrent
CLI invocations (e.g., two `openclaw configure` commands running simultaneously).
The locking is file-level using a `.lock` file.

JSON5 was chosen over JSON for its comment support — users frequently annotate
their config with explanations. The Zod validation runs after JSON5 parse and
produces actionable error messages.


## Cross-References


- `secrets/` — SecretRef encryption and resolution
- `agents/` — model catalog, auth profiles, session overrides
- `plugins/` — plugin config parsing (delegated to channel/provider plugins)
- All modules read config via `loadConfig()` — it is the dependency root
