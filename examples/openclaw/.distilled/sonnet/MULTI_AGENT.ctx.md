---
module: architecture/MULTI_AGENT
type: architecture
purpose: Multi-agent routing, bindings, agent isolation, sub-agents, per-agent sandbox and tool policy
affects: [agents, sessions, channels, tasks, plugins]

tags: [ctx/architecture]
---

## Overview


A single Gateway can run **multiple isolated agents** simultaneously. Each agent
has its own workspace, session store, auth profiles, and persona. Inbound messages
are routed to agents via **bindings** — deterministic rules that match on channel,
account, peer, guild, or team. Sub-agents extend this by spawning background agent
runs from within an existing agent turn.


## Agent Isolation


Each agent is a fully isolated "brain":

| Resource | Per-agent path |
|----------|---------------|
| Workspace | `~/.openclaw/workspace-<agentId>` (or configured path) |
| Auth profiles | `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` |
| Session store | `~/.openclaw/agents/<agentId>/sessions/sessions.json` |
| Transcripts | `~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl` |
| Skills | `<workspace>/skills` + shared `~/.openclaw/skills` |

**Never reuse `agentDir` across agents** — causes auth/session collisions.


## Binding Rules


Bindings are **deterministic** — most-specific match wins. Priority order:

1. `peer` match (exact DM/group/channel id) — **always wins**
2. `parentPeer` match (thread inheritance)
3. `guildId + roles` (Discord role routing)
4. `guildId` (Discord guild)
5. `teamId` (Slack team)
6. `accountId` match for a channel
7. Channel-wide match (`accountId: "*"`)
8. Fallback to default agent (`agents.list[].default`, else first, else `main`)

Multiple fields in a binding = AND semantics (all must match).

```json5
// config: ~/.openclaw/openclaw.json
{
  agents: {
    list: [
      { id: "chat",  workspace: "~/.openclaw/workspace-chat",  model: "anthropic/claude-sonnet-4-6" },
      { id: "deep",  workspace: "~/.openclaw/workspace-deep",  model: "anthropic/claude-opus-4-6" },
      { id: "family", workspace: "~/.openclaw/workspace-family" },
    ],
  },
  bindings: [
    // Peer binding always wins over channel-wide
    { agentId: "deep", match: { channel: "whatsapp", peer: { kind: "direct", id: "+15551234567" } } },
    // Channel-wide fallback
    { agentId: "chat", match: { channel: "whatsapp" } },
    // Different bot per agent on Discord
    { agentId: "chat",   match: { channel: "discord", accountId: "default" } },
    { agentId: "family", match: { channel: "discord", accountId: "family-bot" } },
    // Group-specific routing
    { agentId: "family", match: { channel: "whatsapp", peer: { kind: "group", id: "120363...@g.us" } } },
  ],
}
```


## Multiple Channel Accounts


Channels supporting multiple accounts (WhatsApp, Telegram, Discord, Slack, Signal, …) use `accountId`:

```bash
openclaw channels login --channel whatsapp --account personal
openclaw channels login --channel whatsapp --account biz
```

`accountId: "*"` in a binding matches all accounts on that channel.
Omitting `accountId` matches the default account only.


## Per-Agent Config


```json5
{
  agents: {
    defaults: {
      model: "anthropic/claude-sonnet-4-6",
      skills: ["github", "weather"],           // shared skill baseline
      subagents: {
        model: "anthropic/claude-haiku-4-5-20251001",  // cheaper model for sub-agents
        maxConcurrent: 8,
        maxSpawnDepth: 2,                      // 1=leaf only, 2=orchestrator pattern
        runTimeoutSeconds: 900,
      },
      sandbox: { mode: "off" },
    },
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: { mode: "all", scope: "agent" },
        tools: {
          allow: ["read", "exec", "sessions_list"],
          deny: ["write", "edit", "apply_patch", "browser"],
        },
        skills: ["docs-search"],               // replaces defaults for this agent
        groupChat: { mentionPatterns: ["@family", "@familybot"] },
      },
    ],
  },
}
```


## Sub-Agents


Sub-agents are background agent runs spawned from within an existing agent turn.
Each runs in its own session (`agent:<agentId>:subagent:<uuid>`) and announces
its result back to the requester channel when done.

**Spawn via tool:**
```typescript
// Inside an agent turn — use sessions_spawn tool
sessions_spawn({
  task: "Research the top 5 AI papers from this week and summarize",
  agentId: "research",         // optional — target another agent
  model: "anthropic/claude-opus-4-6",  // optional override
  thinking: "high",
  runTimeoutSeconds: 600,
  thread: true,                // bind to channel thread (Discord supported)
  mode: "session",             // session | run
  cleanup: "keep",             // keep | delete
  sandbox: "inherit",          // inherit | require
})
→ { status: "accepted", runId, childSessionKey }
```

**Spawn via slash command:**
```
/subagents spawn research "Research AI papers this week" --model anthropic/claude-opus-4-6
/subagents list
/subagents kill <id|all>
/subagents log <id> [limit] [tools]
/subagents info <id>
/subagents send <id> <message>
/subagents steer <id> <message>
```

**Nesting depth:**
| Depth | Session key | Role | Can spawn? |
|-------|------------|------|-----------|
| 0 | `agent:<id>:main` | Main agent | Always |
| 1 | `agent:<id>:subagent:<uuid>` | Sub-agent / orchestrator | Only if `maxSpawnDepth >= 2` |
| 2 | `agent:<id>:subagent:<uuid>:subagent:<uuid>` | Leaf worker | Never |

**Announce chain:** depth-2 → announces to depth-1 → synthesizes → announces to main → user.

**Sub-agent context:** only `AGENTS.md` + `TOOLS.md` are injected (no `SOUL.md`, `IDENTITY.md`, `USER.md`, etc.).

**Tool policy:** sub-agents get all tools EXCEPT `sessions_*` and system tools by default.
Depth-1 orchestrators (when `maxSpawnDepth >= 2`) additionally receive `sessions_spawn`, `subagents`, `sessions_list`, `sessions_history`.

**Cost note:** each sub-agent has its own context and token usage. Set `agents.defaults.subagents.model` to a cheaper model.

**Auto-archive:** sub-agent sessions archived after `agents.defaults.subagents.archiveAfterMinutes` (default 60min).


## Cross-Agent Memory Search


One agent can search another's QMD session transcripts:

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        qmd: {
          extraCollections: [{ path: "~/agents/family/sessions", name: "family-sessions" }],
        },
      },
    },
  },
}
```


## Agent-to-Agent Messaging


Off by default. Enable explicitly with allowlist:

```json5
{
  tools: {
    agentToAgent: {
      enabled: true,
      allow: ["main", "research", "family"],
    },
  },
}
```


## Affected Modules


- [[modules/agents.ctx|agents]] — agent execution, model selection, workspace per agent
- [[modules/sessions.ctx|sessions]] — session key patterns, agent isolation
- [[modules/channels.ctx|channels]] — DM allowlists, group routing, accountId per channel
- [[modules/tasks.ctx|tasks]] — sub-agent background task tracking, cron isolation
- [[architecture/AGENT_RUNTIME.ctx|AGENT_RUNTIME]] — runtime internals, workspace, hook points
- [[architecture/AGENT_PIPELINE.ctx|AGENT_PIPELINE]] — single-agent pipeline detail
