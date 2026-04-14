---
module: architecture/message-flow
type: architecture
purpose: End-to-end message flow from inbound channel message to agent response delivery
affects: [channels, gateway, agents, auto-reply, sessions, plugins, hooks]
---

## Overview  <!-- all-tiers -->

Every user message travels through 4 stages:
**Inbound → Routing → Agent Execution → Delivery**

All stages are synchronous within a session (no concurrent processing per session key).

## Full Flow  <!-- all-tiers -->

```
┌─────────────────────────────────────────────────────────┐
│ 1. INBOUND                                              │
│  External service (Discord, Telegram, WhatsApp, …)      │
│    ↓ webhook / polling                                  │
│  ChannelPlugin.outbound.receiveHook()                   │
│    → normalize to internal message format               │
│    → derive session key: "<channelId>/<peerId>"         │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────↓────────────────────────────────┐
│ 2. ROUTING & ALLOWLIST                                  │
│  DM allowlist check (security/pairing)                  │
│    → if unknown sender: offer pairing or drop           │
│  Session key → agent assignment (from config.agents)    │
│  Load session overrides (model, auth profile)           │
│  Load session transcript (JSONL append)                 │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────↓────────────────────────────────┐
│ 3. AGENT EXECUTION                                      │
│  agents/agent-command.ts → agentCommand()               │
│    → resolve model + provider (4-level cascade)         │
│    → load workspace skills snapshot                     │
│    → assemble system prompt                             │
│    → spawn Pi agent via ACP                             │
│    → stream blocks + tool calls                         │
│    → execute tools (browser, canvas, sessions, …)       │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────↓────────────────────────────────┐
│ 4. DELIVERY                                             │
│  auto-reply/reply.ts → getReplyFromConfig()             │
│    → expand reply template variables                    │
│    → execute pre-delivery hooks (webhooks)              │
│    → ChannelPlugin.outbound.send() to origin channel   │
│    → execute post-delivery hooks                        │
└─────────────────────────────────────────────────────────┘
```

## Rules  <!-- all-tiers -->

1. Agents **never** call channel outbound directly — only via `auto-reply/`
2. DM allowlist check happens **before** any agent dispatch
3. Session transcript is **appended** after delivery, never before
4. One active agent invocation per session key at a time

## Error Handling  <!-- sonnet+ -->

| Stage | Error | Behavior |
|-------|-------|---------|
| Inbound | Channel webhook fails | Channel plugin catches, logs, retries |
| Routing | Unknown sender | Pairing offer (if plugin supports) or drop |
| Agent | Model rate limit | Retry with fallback model from cascade |
| Agent | Tool failure | Agent receives error text, may retry |
| Delivery | Channel send fails | Logged as error, not retried automatically |

## Session Concurrency  <!-- sonnet+ -->

OpenClaw processes one message per session key at a time. If a second message
arrives for the same session while an agent is running, it is queued.

This is by design: agents have access to the session transcript, so concurrent
execution would cause race conditions on transcript reads.

## Affected Modules  <!-- all-tiers -->

[[modules/channels.ctx|channels]] → [[modules/sessions.ctx|sessions]] → [[modules/agents.ctx|agents]] → [[modules/acp.ctx|acp]] → [[modules/auto-reply.ctx|auto-reply]] → [[modules/hooks.ctx|hooks]]

- [[modules/gateway.ctx|gateway]] — entry point for inbound WebSocket messages
- [[modules/plugins.ctx|plugins]] — channel plugin dispatch at inbound and delivery stages
