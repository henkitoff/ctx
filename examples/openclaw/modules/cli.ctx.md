---
module: modules/cli
type: codebase
depends_on: [config, infra]
depended_by: []
provides: [runCli, createDefaultDeps, buildProgramFromDescriptors]
invariants:
  - "CLI is the entry point — it wires DI deps but contains no business logic"
  - "All command implementations live in src/commands/ — never inline in CLI"
keywords: [cli, entry-point, commands, argv, program, di, deps]
---

## Purpose  <!-- all-tiers -->

The `cli` module is the **command-line program builder**: it parses argv,
wires dependency injection, registers all subcommands, and routes execution
to the appropriate handler in `src/commands/`.

Key components:
- **`program/`** — Command registry and program builder
- **`deps.ts`** — DI container (ports, config, runtime)
- **`profile.ts`** — CLI profile selection and env setup
- **`argv.ts`** — Argv normalization
- **`run-main.ts`** — Main CLI entry point

## Public API  <!-- all-tiers -->

| Export | Type | Purpose |
|--------|------|---------|
| `runCli` | fn | Main CLI entry — call from `entry.ts` |
| `createDefaultDeps` | fn | Build default DI container |
| `buildProgramFromDescriptors` | fn | Register commands from descriptors |
| `registerCommandGroups` | fn | Register all command groups |

## Invariants  <!-- all-tiers -->

1. CLI is **wiring only** — no business logic inside `src/cli/`
2. All implementations in `src/commands/` — CLI just registers and routes
3. DI deps are created once and passed down — no singletons in commands

## Registered Commands  <!-- all-tiers -->

50+ top-level commands. Grouped by domain:

**Setup & Config**
| Command | Purpose |
|---------|---------|
| `onboard` | Full interactive setup (auth, daemon, channels, skills) |
| `configure` | Wizard for models, channels, gateway binding |
| `setup <plugin>` | Plugin-specific interactive setup |
| `config get/set/unset` | Non-interactive config helpers |
| `doctor` | Health checks + quick fixes for config and gateway |
| `reset` | Reset local config/state (configurable scope) |
| `update` | Update CLI to latest version |
| `completion` | Generate shell completion scripts |

**Agents & Messaging**
| Command | Purpose |
|---------|---------|
| `agent` | Execute single agent turn (--agent, --thinking, --background) |
| `agents list/add/delete/bindings` | Manage isolated agent identities |
| `message send` | Send to any channel (text, media, reactions, threads) |
| `directory` | Look up self, peers, group IDs across channels |
| `pairing` | Approve DM pairing requests |
| `approvals` | Manage exec-approval allowlists |
| `status` | Session health, recent recipients, usage |

**Models & Inference**
| Command | Purpose |
|---------|---------|
| `models list/status/set` | List, probe, set default model |
| `models auth` | Authenticate with provider |
| `models scan` | Discover available models from configured providers |
| `infer` / `capability` | Image gen, transcription, TTS, video, embeddings, web search |

**Channels**
| Command | Purpose |
|---------|---------|
| `channels add/remove` | Connect / disconnect a channel account |
| `channels status --probe` | Health check all connected channels |
| `channels logs` | Stream channel-level logs |

**Gateway & Services**
| Command | Purpose |
|---------|---------|
| `gateway` | Run gateway (foreground) or manage as service |
| `gateway install/start/stop/restart` | Daemon lifecycle (launchd/systemd/schtasks) |
| `gateway status [--deep]` | Runtime health, RPC probe |
| `gateway call` | Raw RPC call to running gateway |
| `gateway usage-cost` | Token usage and cost report |
| `logs --follow` | Tail gateway file logs |
| `node run/install/status` | Headless node lifecycle on remote device |
| `nodes status/approve/reject` | Manage paired device nodes |
| `nodes invoke/camera/canvas/screen/location` | Invoke node hardware capabilities |

**Browser Control**
| Command | Purpose |
|---------|---------|
| `browser start/stop/status` | Chrome/Brave/Edge control |
| `browser navigate/click/type` | Page interaction |
| `browser screenshot/snapshot` | Capture page state |
| `browser tabs/open/close` | Tab management |
| `browser evaluate/console` | JS execution in browser |

**Memory & Knowledge**
| Command | Purpose |
|---------|---------|
| `memory index/search/status` | Vector memory management |
| `memory promote <file>` | Add file to memory index scope |
| `wiki ingest/compile/lint/search` | Knowledge base lifecycle |
| `wiki bridge import/obsidian` | Import from Obsidian vault |
| `sessions list` | List stored conversations |

**Tasks & Automation**
| Command | Purpose |
|---------|---------|
| `tasks list/show/cancel` | Background task management |
| `tasks audit` | Cost + usage audit for background runs |
| `tasks flow list/run` | Multi-step flow pipelines |
| `cron add/rm/enable/disable` | Cron job management |
| `cron list/status/runs` | Cron inspection + history |
| `webhooks gmail/run` | Webhook helpers |

**Plugins, Skills & Hooks**
| Command | Purpose |
|---------|---------|
| `plugins install/enable/disable` | Plugin lifecycle |
| `plugins list/doctor` | Inspect and validate plugins |
| `skills install/update/list` | Manage skill markdown files |
| `hooks enable/disable/list` | Manage internal agent hooks |

**Integration & Dev**
| Command | Purpose |
|---------|---------|
| `acp` | Run ACP bridge (connects IDEs to Gateway) |
| `mcp` | Manage MCP server definitions; expose channels via MCP stdio |
| `sandbox list/recreate` | Manage sandbox runtimes |
| `security` | Audit config and state for security issues |
| `secrets reload/audit` | Manage SecretRefs |
| `tui` | Open terminal UI connected to Gateway |
| `qr` | Generate mobile pairing QR code |
| `dns` | Wide-area discovery DNS helpers |
| `docs` | Search live OpenClaw documentation |

## Key Patterns  <!-- sonnet+ -->

**Command descriptor pattern:**
```typescript
// CLI registers a descriptor — not the implementation
const agentCommandDescriptor = {
  name: "agent",
  description: "Execute an agent command",
  options: [...],
  handler: (opts, deps) => commandAgent(opts, deps),  // delegates to commands/
}
registerCommandGroups(program, [agentCommandDescriptor, ...])
```

**DI container:**
```typescript
const deps = createDefaultDeps({
  configPath: resolvedConfigPath,
  gatewayPort: resolvedPort,
})
// deps flows through to every command handler
// enables testing without global state
```

## Cross-References  <!-- all-tiers -->

- `commands/` — all command implementations (not a separate .ctx module)
- [[modules/config.ctx|config]] — config path resolution at startup
- [[modules/infra.ctx|infra]] — port checking, binary provisioning
- [[modules/gateway.ctx|gateway]] — CLI manages gateway daemon lifecycle
