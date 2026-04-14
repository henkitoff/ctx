---
module: modules/auto-reply
type: codebase
depends_on: [channels, config, plugins]
depended_by: [gateway]
provides: [getReplyFromConfig, ReplyPayload]
invariants:
  - "Auto-reply delivery is the ONLY path for sending responses back to channels"
  - "Template variable expansion happens before delivery, not in the agent"
keywords: [auto-reply, routing, delivery, templating, webhooks, standing-orders]
---

## Purpose


The `auto-reply` module is the **message delivery layer**: after an agent
produces a response, auto-reply applies templating, executes webhooks, and
delivers the final content back to the originating channel via the channel
plugin's outbound adapter.

Key components:
- **`reply/`** — Reply execution and delivery
- **`templating.ts`** — Template variable expansion (`{{session.peer}}`, etc.)
- **`reply-payload.ts`** — `ReplyPayload` schema
- **`delivery.ts`** — Dispatch back to channel plugin


## Public API


| Export | Type | Purpose |
|--------|------|---------|
| `getReplyFromConfig` | fn | Resolve and execute reply for a session |
| `ReplyPayload` | type | Structured reply with content + metadata |


## Invariants


1. Auto-reply is the **only** path for sending responses to channels — agents don't call channels directly
2. Template expansion happens **before** delivery
3. Webhook hooks fire **after** channel delivery, not before


## Key Patterns


**Delivery flow:**
```typescript
// After agent produces response:
const payload = await getReplyFromConfig(sessionKey, agentResponse, config)
// 1. Apply template (if configured)
// 2. Execute pre-delivery hooks (webhooks, standing orders)
// 3. Send via channel outbound adapter
// 4. Execute post-delivery hooks
```

**Template variables (available in reply templates):**
- `{{session.key}}` — full session key
- `{{session.peer}}` — peer ID (user/group)
- `{{session.channel}}` — channel ID
- `{{reply.content}}` — agent reply text
- `{{agent.id}}` — agent that produced the reply


## Cross-References


- `channels/` — delivery via `ChannelOutboundAdapter.send()`
- `hooks/` — post-delivery hook dispatch
- `config/` — reply template config, webhook URLs
- Architecture: see architecture/MESSAGE_FLOW.ctx.md for full delivery flow
