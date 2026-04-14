---
module: modules/channels
type: codebase
depends_on: [plugins, config, security]
depended_by: [agents, gateway, auto-reply]
provides: [ChannelPlugin, ChannelOutboundAdapter, ChannelId, resolveChannelApprovalAdapter]
invariants:
  - "Each channel plugin implements only the adapters it supports — all adapters optional"
  - "Session key always encodes channel + peer: <channelId>/<peerId>"
  - "DM allowlist check happens before any agent dispatch"
keywords: [channels, discord, telegram, whatsapp, slack, adapters, pairing, outbound]
---

## Purpose


The `channels` module provides the **channel plugin abstraction**: a unified
interface over all messaging platforms (Discord, Telegram, WhatsApp, Slack,
iMessage, and 20+ more). Each channel is a plugin implementing a standard set
of optional adapters.

Key components:
- **`plugins/types.plugin.ts`** — Full `ChannelPlugin` contract
- **`plugins/types.adapters.ts`** — Individual adapter types
- **`allowlists/`** — DM allowlisting and pairing enforcement
- **`web/`** — WebChat transport


## Public API


| Export | Type | Purpose |
|--------|------|---------|
| `ChannelPlugin` | type | Complete channel plugin contract |
| `ChannelId` | type | String brand for channel identifiers |
| `ChannelOutboundAdapter` | type | Send/receive adapter contract |
| `ChannelAuthAdapter` | type | Login/logout adapter contract |
| `ChannelStatusAdapter` | type | Health check adapter contract |
| `resolveChannelApprovalAdapter` | fn | Get approval capability for channel |


## Invariants


1. All adapters are **optional** — a channel implements only what it supports
2. Session key = `<channelId>/<peerId>` — encodes routing for agents
3. DM allowlist check happens **before** any agent dispatch
4. `ChannelPlugin.outbound.receiveHook()` is the single inbound entry point


## Channel Adapter Contracts


| Adapter | Responsibility | Required? |
|---------|---------------|----------|
| `config` | Parse/validate channel config | Yes |
| `outbound` | Send messages, receive webhooks | Core |
| `auth` | Login/logout flows | If auth needed |
| `status` | Connection health, diagnostics | Recommended |
| `pairing` | Accept/reject unknown senders | If DM policy enforced |
| `setup` | Interactive onboarding wizard | Recommended |
| `commands` | Channel-specific slash commands | Optional |
| `gateway` | Custom RPC methods on gateway | Optional |
| `approvalCapability` | Integration with approval workflows | Optional |


## Supported Channels


26 platforms bundled. Setup method and capability level vary:

| Channel | Setup | Text | Media | Reactions | Notes |
|---------|-------|------|-------|-----------|-------|
| Telegram | Bot token | ✓ | ✓ | ✓ | Recommended first channel |
| WhatsApp | QR pairing | ✓ | ✓ | ✓ | Most popular; Baileys lib |
| Discord | Bot token | ✓ | ✓ | ✓ | Slash commands + voice |
| Slack | Bolt SDK | ✓ | ✓ | ✓ | Enterprise; OAuth |
| BlueBubbles | REST API | ✓ | ✓ | ✓ | iMessage via macOS; full feature |
| Signal | signal-cli | ✓ | ✓ | — | Privacy-focused |
| Matrix | WebSocket | ✓ | ✓ | ✓ | Self-hosted friendly |
| Microsoft Teams | Webhook | ✓ | ✓ | — | Enterprise |
| Google Chat | HTTP webhook | ✓ | — | — | Workspace bots |
| iMessage (legacy) | imsg CLI | ✓ | — | — | macOS only; limited |
| Mattermost | WebSocket | ✓ | ✓ | ✓ | Self-hosted |
| Nostr | NIP-04 | ✓ | — | — | Decentralized |
| LINE | Token | ✓ | ✓ | — | APAC |
| WeChat | QR pairing | ✓ | ✓ | — | China |
| Zalo | Token | ✓ | ✓ | — | Vietnam |
| Zalo Personal | QR pairing | ✓ | ✓ | — | Vietnam personal |
| Feishu/Lark | WebSocket | ✓ | ✓ | ✓ | Collaboration |
| IRC | Server/CLI | ✓ | — | — | Legacy |
| Nextcloud Talk | WebSocket | ✓ | ✓ | — | Self-hosted |
| Synology Chat | Webhook | ✓ | — | — | NAS integration |
| Tlon | WebSocket | ✓ | — | — | Urbit-based |
| Twitch | — | ✓ | — | — | Streaming chat |
| Voice Call | Plugin | — | — | — | Audio only |
| WebChat | WS (built-in) | ✓ | ✓ | — | Browser UI; always available |
| QQ Bot | Token | ✓ | ✓ | — | China |
| Zulip | Webhook | ✓ | ✓ | — | Team messaging |


## Cross-References


- [[modules/plugins.ctx|plugins]] — Channel plugins loaded via plugin registry
- [[modules/sessions.ctx|sessions]] — Session key derivation from channel + peer
- [[modules/auto-reply.ctx|auto-reply]] — Delivery back to channel after agent response
- [[modules/nodes.ctx|nodes]] — Nodes expose additional hardware capabilities per channel session
- Architecture: see [[architecture/MESSAGE_FLOW.ctx|MESSAGE_FLOW]] for inbound/outbound flow
