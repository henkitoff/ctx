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


## Affected Modules


This is a navigation reference only — it does not implement any module.
Every module in the openclaw `.ctx` is listed in the tables above.
