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



### 1. Session Store (`sessions.json`)


Key/value map: `sessionKey → SessionEntry`. Small, mutable.

**Location:** `~/.openclaw/agents/<agentId>/sessions/sessions.json`

**Key `SessionEntry` fields:**
| Field | Description |
|-------|-------------|
| `sessionId` | Current transcript id (filename derived from this) |
| `updatedAt` | Last activity timestamp |
| `chatType` | `direct \| group \| room` |
| `compactionCount` | How many times auto-compaction completed for this key |
| `memoryFlushAt` | Timestamp of last pre-compaction memory flush |
| `contextTokens` | Runtime estimate (reporting only, not a strict guarantee) |
| `inputTokens / outputTokens` | Rolling counters |
| `providerOverride / modelOverride` | Per-session model selection |
| `thinkingLevel / verboseLevel` | Toggle state |
| `sendPolicy` | Per-session override |


### 2. Transcript (`<sessionId>.jsonl`)


Append-only transcript with **tree structure** (entries have `id` + `parentId`).

**Location:** `~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`

**Entry types:**
| Type | Description |
|------|-------------|
| `message` | User/assistant/toolResult messages |
| `custom_message` | Extension-injected messages that enter model context (can be hidden from UI) |
| `custom` | Extension state that does NOT enter model context |
| `compaction` | Persisted compaction summary with `firstKeptEntryId` and `tokensBefore` |
| `branch_summary` | Persisted summary when navigating a tree branch |


## Session Lifecycle


**Session ID rotation triggers:**
- `/new` or `/reset` command
- Daily reset (4:00 AM gateway-host local time, on next message)
- Idle expiry (`session.reset.idleMinutes`) — whichever of daily or idle fires first wins
- Thread parent fork guard (`session.parentForkMaxTokens`, default 100000) — if parent session is too large, new thread starts fresh


## Compaction


Compaction summarizes older conversation into a persisted `compaction` entry and keeps recent messages. Future turns see: compaction summary + messages after `firstKeptEntryId`.

**Auto-compaction triggers (Pi runtime):**
1. **Overflow recovery** — model returns context overflow error → compact → retry
2. **Threshold maintenance** — after successful turn when: `contextTokens > contextWindow - reserveTokens`

**Tool call pairing rule:** compaction boundary shifts to keep assistant tool calls paired with their toolResult. Aborted/error tool-call blocks do not hold the split open.

**Compaction settings:**
```json5
{
  agents: {
    defaults: {
      compaction: {
        enabled: true,
        reserveTokens: 16384,         // headroom for prompts + next output
        keepRecentTokens: 20000,
        reserveTokensFloor: 20000,    // OpenClaw safety floor (bumps if lower)
        provider: "my-plugin-id",     // optional: pluggable compaction provider
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 4000,  // flush when this close to compaction threshold
        },
      },
    },
  },
}
```

**Pre-compaction memory flush:** when `contextTokens` crosses the soft threshold, a silent `NO_REPLY` turn runs to write durable state to `memory/YYYY-MM-DD.md` before compaction erases it. Tracked in `memoryFlushAt` / `memoryFlushCompactionCount`.

**Pluggable compaction providers:** plugins can register via `registerCompactionProvider()`. Set `agents.defaults.compaction.provider` to delegate summarization. Falls back to built-in LLM summarization automatically on failure.


## Session Store Maintenance


```json5
{
  session: {
    maintenance: {
      mode: "warn",           // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
      maxDiskBytes: "5gb",
      highWaterBytes: "80%",  // cleanup target (% of maxDiskBytes)
    },
  },
}
```

Enforcement order (when `mode: "enforce"`):
1. Remove oldest archived or orphan transcript artifacts
2. If still above target, evict oldest session entries + their transcript files
3. Continue until at or below `highWaterBytes`

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce
```


## Silent Housekeeping (`NO_REPLY`)


Convention for background turns that should not produce user-visible output:

- Assistant starts output with exact token `NO_REPLY` or `no_reply` (case-insensitive)
- OpenClaw strips/suppresses delivery
- Streaming suppression also prevents partial output leaking mid-turn
- Used by: pre-compaction memory flush, dreaming sweeps, background cron tasks


## CLI


```bash
openclaw sessions list [--json]
openclaw sessions show <sessionKey>
openclaw sessions cleanup [--dry-run] [--enforce]
openclaw sessions reset <sessionKey>
openclaw status   # shows active session key, token counts, compaction state
```


## Cross-References


- [[modules/agents.ctx|agents]] — uses session key for agent assignment, model override, memory flush
- [[modules/channels.ctx|channels]] — derives session key from channel + peer on message receipt
- [[modules/config.ctx|config]] — session overrides keyed by session key
- [[modules/memory.ctx|memory]] — pre-compaction flush writes to `memory/YYYY-MM-DD.md`
- [[architecture/AGENT_RUNTIME.ctx|AGENT_RUNTIME]] — agent loop stage 1 (session resolution), compaction, streaming
- [[architecture/MULTI_AGENT.ctx|MULTI_AGENT]] — sub-agent session key patterns (depth 0/1/2)
