---
module: modules/sessions
type: codebase
depends_on: [config]
depended_by: [agents, gateway, channels]
provides: [deriveSessionChatType, SessionKey, SessionKeyChatType]
invariants:
  - "Transcript is append-only JSONL — never rewrite or truncate entries"
  - "Always use deriveSessionKey() — never construct session key strings ad-hoc"
  - "Gateway is the authority — UIs must query Gateway for session state, not read local files"
  - "Compaction is persistent — unlike pruning which is in-memory, compaction entries survive restarts"
keywords: [sessions, session-key, chat-type, dm, group, transcript, compaction, JSONL, session-store]

tags: [ctx/module]
---

## Purpose


The `sessions` module defines the **session model**: how inbound messages map
to sessions, session key derivation, chat type classification, and the two-layer
persistence system (session store + transcript).

| Export | Type | Purpose |
|--------|------|---------|
| `SessionKey` | type | Branded session key string |
| `SessionKeyChatType` | type | `"direct" \| "group" \| "room"` |
| `deriveSessionChatType` | fn | Derive chat type from session key |
| `deriveSessionChatTypeFromKey` | fn | Same, from raw session key string |


## Invariants


1. **Append-only transcript** — JSONL file is never rewritten or truncated
2. **Use `deriveSessionKey()`** — never construct session key strings manually
3. **Gateway is authority** — in remote mode, session files are on remote host; query Gateway via API
4. **Compaction is persistent** — compaction entries in JSONL survive restarts (unlike session pruning which is in-memory)
5. **Tool call pairs** — when splitting for compaction, tool calls are always kept paired with their toolResult (boundary shifts if needed)
6. **Daily reset** — new sessionId created on next message after 4:00 AM gateway-host local time


## Session Keys


Session key patterns (canonical; managed by `deriveSessionKey()`):

```
agent:<agentId>:main                         ← direct chat (per agent)
agent:<agentId>:<channel>:group:<id>         ← group chat
agent:<agentId>:<channel>:channel:<id>       ← Discord/Slack channel
agent:<agentId>:subagent:<uuid>              ← sub-agent session
agent:<agentId>:subagent:<uuid>:subagent:<uuid>  ← depth-2 sub-agent
cron:<job.id>                                ← cron job run
hook:<uuid>                                  ← webhook trigger
```

Chat type derivation: `direct | group | room` — derived from the session key format.


## Two Persistence Layers



## Cross-References


- [[modules/agents.ctx|agents]] — uses session key for agent assignment, model override, memory flush
- [[modules/channels.ctx|channels]] — derives session key from channel + peer on message receipt
- [[modules/config.ctx|config]] — session overrides keyed by session key
- [[modules/memory.ctx|memory]] — pre-compaction flush writes to `memory/YYYY-MM-DD.md`
- [[architecture/AGENT_RUNTIME.ctx|AGENT_RUNTIME]] — agent loop stage 1 (session resolution), compaction, streaming
- [[architecture/MULTI_AGENT.ctx|MULTI_AGENT]] — sub-agent session key patterns (depth 0/1/2)
