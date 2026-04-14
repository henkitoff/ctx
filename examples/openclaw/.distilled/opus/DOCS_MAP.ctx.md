---
module: architecture/DOCS_MAP
type: architecture
purpose: Complete OpenClaw documentation map — agent navigation reference for all docs pages
affects: [all modules]

tags: [ctx/architecture]
---

## Overview


Full documentation map for openclaw/openclaw. Agents read this to discover which
documentation page covers a topic before reading the relevant `.ctx.md` module doc.
Source: https://docs.openclaw.ai/start/hubs


## Core Concepts


| Topic | Doc URL | .ctx coverage |
|-------|---------|--------------|
| Gateway architecture | /concepts/architecture | architecture/GATEWAY_PROTOCOL.ctx.md |
| Agent runtime | /concepts/agent | architecture/AGENT_RUNTIME.ctx.md |
| Agent workspace | /concepts/agent-workspace | architecture/AGENT_RUNTIME.ctx.md |
| Agent loop | /concepts/agent-loop | architecture/AGENT_RUNTIME.ctx.md |
| Multi-agent routing | /concepts/multi-agent | architecture/MULTI_AGENT.ctx.md |
| Memory system | /concepts/memory | modules/memory.ctx.md |
| Sessions | /concepts/session | modules/sessions.ctx.md |
| Compaction | /concepts/compaction | architecture/AGENT_RUNTIME.ctx.md |
| Context assembly | /concepts/context | architecture/AGENT_RUNTIME.ctx.md |
| Model failover | /concepts/model-failover | modules/agents.ctx.md |
| Queue / steering | /concepts/queue | modules/tasks.ctx.md |
| Streaming + chunking | /concepts/streaming | modules/gateway.ctx.md |
| Presence | /concepts/presence | modules/gateway.ctx.md |
| OAuth | /concepts/oauth | modules/secrets.ctx.md |
| Features overview | /concepts/features | — (this doc) |


## Channels


| Channel | Doc URL | Setup |
|---------|---------|-------|
| WhatsApp | /channels/whatsapp | QR pairing (Baileys) |
| Telegram | /channels/telegram | Bot token |
| Discord | /channels/discord | Bot token + Intent |
| Slack | /channels/slack | Bolt SDK / OAuth |
| Signal | /channels/signal | signal-cli |
| BlueBubbles (iMessage) | /channels/bluebubbles | REST API on macOS |
| Mattermost | /channels/mattermost | WebSocket |
| Matrix | /channels/matrix | WebSocket |
| Microsoft Teams | /channels/teams | Webhook |
| Google Chat | /channels/googlechat | HTTP webhook |
| QQ Bot | /channels/qqbot | Token |
| iMessage legacy | /channels/imessage | imsg CLI |
| IRC | /channels/irc | Server/CLI |
| LINE | /channels/line | Token |
| Nostr | /channels/nostr | NIP-04 |
| Zalo | /channels/zalo | Token |
| Zalo Personal | /channels/zalouser | QR pairing |
| Feishu/Lark | /channels/feishu | WebSocket |
| Synology Chat | /channels/synology | Webhook |
| Nextcloud Talk | /channels/nextcloud | WebSocket |
| WebChat | /web/webchat | Built-in |
| Channel routing | /channels/channel-routing | modules/channels.ctx.md |
| Group messages | /channels/groups | modules/channels.ctx.md |


## Gateway & Operations


| Topic | Doc URL | .ctx coverage |
|-------|---------|--------------|
| Gateway runbook | /gateway | modules/gateway.ctx.md |
| Network model | /gateway/network-model | modules/gateway.ctx.md |
| Pairing (devices) | /gateway/pairing | modules/nodes.ctx.md |
| Security | /gateway/security | modules/gateway.ctx.md |
| Sandboxing | /gateway/sandboxing | modules/sandbox.ctx.md |
| Remote access | /gateway/remote | modules/gateway.ctx.md |
| Tailscale | /gateway/tailscale | modules/gateway.ctx.md |
| Logging | /gateway/logging | modules/gateway.ctx.md |
| Discovery | /gateway/discovery | modules/gateway.ctx.md |
| Configuration | /gateway/configuration | modules/config.ctx.md |
| Configuration examples | /gateway/configuration-examples | modules/config.ctx.md |
| Doctor | /gateway/doctor | modules/cli.ctx.md |
| Health | /gateway/health | modules/gateway.ctx.md |
| Heartbeat | /gateway/heartbeat | modules/tasks.ctx.md |


## Tools & Automation


| Topic | Doc URL | .ctx coverage |
|-------|---------|--------------|
| Tools overview | /tools | modules/agents.ctx.md |
| exec tool | /tools/exec | modules/agents.ctx.md |
| Browser tool | /tools/browser | modules/nodes.ctx.md |
| Sub-agents | /tools/subagents | architecture/MULTI_AGENT.ctx.md |
| Skills | /tools/skills | architecture/AGENT_RUNTIME.ctx.md |
| ClawHub (skills registry) | /tools/clawhub | architecture/AGENT_RUNTIME.ctx.md |
| Skills config | /tools/skills-config | architecture/AGENT_RUNTIME.ctx.md |
| Slash commands | /tools/slash-commands | modules/cli.ctx.md |
| Thinking / verbose | /tools/thinking | modules/agents.ctx.md |
| Cron jobs | /automation/cron-jobs | modules/tasks.ctx.md |
| Automation & Tasks | /automation | modules/tasks.ctx.md |
| Agent send CLI | /tools/agent-send | modules/cli.ctx.md |
| Terminal UI | /web/tui | modules/cli.ctx.md |
| OpenProse | /prose | — |
| Capability cookbook | /tools/capability-cookbook | modules/plugins.ctx.md |


## Nodes, Media, Voice


| Topic | Doc URL | .ctx coverage |
|-------|---------|--------------|
| Nodes overview | /nodes | modules/nodes.ctx.md |
| Camera | /nodes/camera | modules/nodes.ctx.md |
| Images | /nodes/images | modules/nodes.ctx.md |
| Audio | /nodes/audio | modules/nodes.ctx.md |
| Location command | /nodes/location-command | modules/nodes.ctx.md |
| Voice wake | /nodes/voicewake | modules/nodes.ctx.md |
| Talk mode | /nodes/talk | modules/nodes.ctx.md |


## Platforms


| Platform | Doc URL |
|----------|---------|
| macOS | /platforms/macos |
| iOS | /platforms/ios |
| Android | /platforms/android |
| Windows (WSL2) | /platforms/windows |
| Linux | /platforms/linux |
| Web surfaces | /web |
| macOS menu bar | /platforms/mac/menu-bar |
| macOS Canvas | /platforms/mac/canvas |
| macOS voice | /platforms/mac/voicewake |
| macOS gateway (launchd) | /platforms/mac/bundled-gateway |


## Plugins & Extensions


| Topic | Doc URL | .ctx coverage |
|-------|---------|--------------|
| Plugins overview | /tools/plugin | modules/plugins.ctx.md |
| Building plugins | /plugins/building-plugins | modules/plugins.ctx.md |
| Plugin manifest | /plugins/manifest | modules/plugins.ctx.md |
| Plugin bundles | /plugins/bundles | modules/plugins.ctx.md |
| Community plugins | /plugins/community | modules/plugins.ctx.md |
| Voice call plugin | /plugins/voice-call | modules/plugins.ctx.md |


## Workspace Templates


Template files injected into agent context on session start:

| File | Purpose | Doc |
|------|---------|-----|
| `AGENTS.md` | Operating instructions + memory | /reference/templates/AGENTS |
| `SOUL.md` | Persona, tone, boundaries | /reference/templates/SOUL |
| `USER.md` | User profile | /reference/templates/USER |
| `IDENTITY.md` | Agent name/vibe/emoji | /reference/templates/IDENTITY |
| `TOOLS.md` | Local tool notes | /reference/templates/TOOLS |
| `HEARTBEAT.md` | Periodic check tasks | /reference/templates/HEARTBEAT |
| `BOOTSTRAP.md` | One-time first-run ritual | /reference/templates/BOOTSTRAP |
| `MEMORY.md` | Long-term memory | /concepts/memory |
| `memory/YYYY-MM-DD.md` | Daily memory log | /concepts/memory |


## Installation


| Method | Doc |
|--------|-----|
| Quick installer (macOS/Linux) | /install |
| Docker | /install/docker |
| Kubernetes | — |
| Nix | /install/nix |
| Fly.io, Hetzner, GCP, Azure | /platforms |
| Updating / rollback | /install/updating |


## Reference


| Topic | Doc URL |
|-------|---------|
| RPC adapters | /reference/rpc |
| Session management (deep dive) | /reference/session-management-compaction |
| Memory configuration | /reference/memory-config |
| Environment variables | /gateway/environment-variables |
| Prompt caching | /reference/prompt-caching |
| Rich output protocol | /reference/rich-output |
| SecretRef credential surface | /reference/secretref |
| Device models | /reference/device-models |
| TypeBox schemas | /concepts/typebox |
| Testing | /reference/test |
| Release policy | /reference/RELEASING |
| Default AGENTS.md | /reference/AGENTS.default |
| Token use & costs | /reference/token-use |
| Transcript hygiene | /reference/transcript-hygiene |
| Troubleshooting | /gateway/troubleshooting |
| FAQ | /help |


## Affected Modules


This is a navigation reference only — it does not implement any module.
Every module in the openclaw `.ctx` is listed in the tables above.
