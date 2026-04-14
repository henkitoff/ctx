# OpenClaw — Agent Entry Point

> **OpenClaw** is a personal AI assistant platform: routes messages from any channel
> (WhatsApp, Telegram, Slack, Discord, iMessage, …) through a plugin-driven gateway
> to LLM agents. TypeScript monorepo, ~6 500 source files, 99 bundled plugins.
>
> Source: https://github.com/openclaw/openclaw

---

## Quick Navigation

| Task | Read first |
|------|-----------|
| Understand end-to-end message flow | [[architecture/MESSAGE_FLOW.ctx\|MESSAGE_FLOW]] |
| Add a new messaging channel | [[modules/channels.ctx\|channels]] + [[architecture/PLUGIN_SYSTEM.ctx\|PLUGIN_SYSTEM]] |
| Add a new LLM provider | [[modules/plugins.ctx\|plugins]] + [[architecture/PLUGIN_SYSTEM.ctx\|PLUGIN_SYSTEM]] |
| **Integrate LM Studio (local LLM)** | **[[modules/lmstudio.ctx\|lmstudio]] + [[architecture/LOCAL_INFERENCE.ctx\|LOCAL_INFERENCE]]** |
| Modify agent execution | [[modules/agents.ctx\|agents]] + [[architecture/AGENT_PIPELINE.ctx\|AGENT_PIPELINE]] |
| Understand agent runtime internals | [[architecture/AGENT_RUNTIME.ctx\|AGENT_RUNTIME]] |
| Set up multi-agent routing | [[architecture/MULTI_AGENT.ctx\|MULTI_AGENT]] |
| Navigate all documentation | [[architecture/DOCS_MAP.ctx\|DOCS_MAP]] |
| Configure sandbox (Docker/SSH/OpenShell) | [[architecture/SANDBOX.ctx\|SANDBOX]] |
| Change gateway RPC protocol | [[modules/gateway.ctx\|gateway]] + [[architecture/GATEWAY_PROTOCOL.ctx\|GATEWAY_PROTOCOL]] |
| Work on memory / wiki / knowledge | [[modules/memory.ctx\|memory]] |
| Work on paired device nodes | [[modules/nodes.ctx\|nodes]] |
| Work on cron / background tasks | [[modules/tasks.ctx\|tasks]] |
| Work on config loading/mutation | [[modules/config.ctx\|config]] |
| Add a CLI command | [[modules/cli.ctx\|cli]] |
| Work on secrets or auth | [[modules/secrets.ctx\|secrets]] |

---

## Tier Selection

| Model | Read from |
|-------|-----------|
| Haiku / fast workers | .distilled/haiku/ |
| Sonnet / manager agents | .distilled/sonnet/ |
| Opus / architect tasks | modules/ + architecture/ |

---

## Critical Invariants

1. **Plugin boundary:** Extensions import ONLY `openclaw/plugin-sdk/*` — never `src/**`
2. **Plugin manifests are source of truth** for capabilities, config schema, auth
3. **Config mutations are atomic** — always use `mutateConfigFile()`, never write directly
4. **Session key** = `<channelId>/<peerId>` — encodes channel routing
5. **Gateway protocol is versioned RPC** — protocol changes require versioning
6. **Secrets use SecretRef** (`{ $ref: "provider/key" }`) — never store plain values in config
7. **Transcript is append-only JSONL** — never rewrite session history
8. **No `any`, no `@ts-nocheck`** — use `unknown` or proper types
9. **Local provider health check:** runs once per session, never per-request — result cached
10. **Model refs carry scheme prefix** (`lmstudio:`, `anthropic:`, `openai:`) — bare names rejected

---

## Package Map

| Package | Files | Purpose |
|---------|-------|---------|
| agents | 1 241 | Agent runtime, model selection, tools, skills |
| infra | 625 | HTTP, TLS, ports, binaries, network |
| gateway | 500 | WebSocket control plane, RPC, auth |
| commands | 451 | CLI + RPC command implementations |
| plugins | 423 | Plugin loading, registry, contracts, hooks |
| auto-reply | 420 | Inbound routing, templating, delivery |
| plugin-sdk | 396 | Public plugin contract surface |
| cli | 350 | CLI program builder, argv routing |
| config | 312 | Config load/validate/mutate/persist |
| channels | 201 | Channel plugin abstraction, adapters |
| cron | 150 | Scheduled tasks with agent isolation |
| secrets | 108 | Crypto, storage, resolution, audit |
| memory-host-sdk | 94 | KV/embeddings host interface |
| shared | 90 | Text, net, formatting utilities |
| security | 78 | TLS, signing, DM policies, pairing |
| media | 58 | Media pipeline, transcoding |
| acp | 61 | Agent Client Protocol (wire format) |
| daemon | 59 | launchd/systemd service lifecycle |
| sessions | 18 | Session model, chat types, ID resolution |
| hooks | 45 | Hook dispatch, bundled hooks |
| lmstudio | — | Local LLM provider plugin (LM Studio integration) |
| memory | — | Vector memory store + wiki knowledge base + Obsidian bridge |
| nodes | — | Paired device management (iOS/Android/headless, camera/screen/location) |
| tasks | — | Background task runs, cron scheduler, multi-step flows |

---

---

## External Lib References

| Library | Entry point | Covers |
|---------|-------------|--------|
| **LM Studio** | [[lmstudio/INDEX\|lmstudio/INDEX.md]] | REST API, TypeScript SDK, Python SDK, CLI |

These are read-only reference docs for external APIs used by openclaw plugins.
The `lmstudio/` reference is consumed by `modules/lmstudio.ctx.md` (provider plugin).

---

## Last Session

Agents read [[knowledge/LATEST.yaml|knowledge/LATEST.yaml]] at session start — current project state, patterns, next hints.

```
knowledge/
├── LATEST.yaml     ← Always read this first
└── TEMPLATE.yaml   ← Copy when creating a new distillate
```

See `.distilled/MANIFEST.json` for token counts per tier:
- haiku: ~19k tokens (25 files)
- sonnet: ~33k tokens (25 files)
- opus: ~39k tokens (25 files)
