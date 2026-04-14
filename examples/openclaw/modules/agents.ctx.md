---
module: modules/agents
type: codebase
depends_on: [plugins, config, acp, channels, gateway, sessions]
depended_by: [commands, gateway]
provides: [agentCommand, AgentHarness, resolveDefaultModelForAgent, buildWorkspaceSkillSnapshot]
invariants:
  - "Agents never call channel adapters directly — route via gateway/auto-reply"
  - "Model selection follows: session override → agent config → global default → fallback"
  - "Skills snapshot is loaded once per session, not per token"
  - "Model ref format: provider/model-id — first slash splits provider from model"
  - "Auth profile pinned per session for cache warmth — rotates only on reset/compaction/cooldown"
keywords: [agent, model, tools, skills, harness, acp, pi-agent, thinking, failover, model-ref, bootstrap]
---

## Purpose  <!-- all-tiers -->

The `agents` module is the **agent execution runtime**: it orchestrates model
selection, skill loading, system prompt assembly, tool dispatch, and Pi agent
spawning via the Agent Client Protocol (ACP).

Key components:
- **`agent-command.ts`** — Main orchestration entry point
- **`model-catalog.ts`** — Model registry, selection, fallback
- **`harness/`** — Execution wrapper types
- **`tools/`** — Built-in tools (browser, canvas, cron, sessions, …)
- **`skills/`** — Workspace skill discovery and loading
- **`auth-profiles/`** — Auth provider credential resolution
- **`pi-embedded-runner/`** — Pi agent-core integration
- **`system-prompt.ts`** — System prompt assembly

## Public API  <!-- all-tiers -->

| Export | Type | Purpose |
|--------|------|---------|
| `agentCommand` | fn | Main entry: execute agent for a session |
| `AgentHarness` | type | Harness carrying session + model context |
| `AnyAgentTool` | type | Union of all built-in tool types |
| `resolveDefaultModelForAgent` | fn | Model selection with fallback |
| `normalizeModelRef` | fn | Normalize model string to canonical form |
| `buildWorkspaceSkillSnapshot` | fn | Discover + load skills for current session |

## Invariants  <!-- all-tiers -->

1. Agents **never** call channel adapters directly — delivery goes via `auto-reply/`
2. Model selection order: session override → agent config → global default → fallback
3. Skill snapshot is loaded **once per session invocation**, not per token/tool
4. Tool execution is synchronous within the agent loop — no concurrent tool calls

## Key Patterns  <!-- sonnet+ -->

**Model selection cascade:**
```typescript
function resolveDefaultModelForAgent(agentId: string, config: OpenClawConfig): ModelRef {
  return (
    config.session?.modelOverride           // 1. per-session user choice
    ?? config.agents?.[agentId]?.model      // 2. per-agent config
    ?? config.defaults?.model               // 3. global default
    ?? FALLBACK_MODEL                       // 4. hardcoded fallback
  )
}
```

**System prompt assembly:**
```typescript
// Contributions from multiple sources, assembled in order:
// 1. Base prompt (from config or default)
// 2. Provider-contributed additions (e.g. Claude's system header)
// 3. Skills listing (workspace skills the agent knows about)
// 4. Active tools listing
```

**Skill snapshot:**
Skills are markdown files in `~/.openclaw/skills/` or workspace.
`buildWorkspaceSkillSnapshot()` reads them once and injects into system prompt.
Mutating skills mid-conversation has no effect until next session.

## Internal Structure  <!-- sonnet+ -->

```
src/agents/
├── agent-command.ts        ← Main entry point
├── model-catalog.ts        ← Registry + selection + fallback
├── system-prompt.ts        ← System prompt assembly
├── harness/                ← Execution wrapper types
├── tools/
│   ├── browser.ts          ← Web browsing tool
│   ├── canvas.ts           ← Canvas A2UI tool
│   ├── cron.ts             ← Schedule tasks from agent
│   └── sessions.ts         ← Cross-session messaging tool
├── skills/
│   ├── snapshot.ts         ← buildWorkspaceSkillSnapshot
│   └── loader.ts           ← Read skill .md files
├── auth-profiles/          ← Credential resolution per provider
├── pi-embedded-runner/     ← Pi agent-core integration
└── acp-spawn.ts            ← Spawn via Agent Client Protocol
```

## Model Ref Format  <!-- sonnet+ -->

```
"provider/model-id"           ← parsed by splitting on the FIRST slash only

Examples:
  "anthropic/claude-sonnet-4-6"
  "openai/gpt-4o"
  "openrouter/moonshotai/kimi-k2"     ← provider prefix required for multi-slash IDs
  "lmstudio:meta-llama/Llama-3.2-3B"  ← scheme:publisher/model for local providers
  "ollama/llama3.1:8b"

Fallback: if provider omitted → try aliases → configured-provider match → default provider
```

## Model Failover  <!-- sonnet+ -->

Two-stage failover on inference errors:

1. **Auth profile rotation** — within current provider (round-robin, cooldowns)
2. **Model fallback** — move to next in `agents.defaults.model.fallbacks`

**Rotation order within a provider:**
- OAuth before API keys; within each type: oldest `lastUsed` first
- Cooldown/disabled profiles move to end
- Auth profile **pinned per session** for cache warmth; rotates only on `/new`, `/reset`, compaction, or cooldown
- Rate limits → exponential backoff: 1 min → 5 min → 25 min → 1 hr (cap)
- Billing failures → long backoff: 5 hr → 24 hr cap

**Fallback chain rules:**
- Requested model always first; configured fallbacks in order
- Advances on: auth failure, rate limit, overload, timeout, billing disable
- Does NOT advance on: context overflow errors (handled by compaction), explicit aborts
- If all candidates fail → `FallbackSummaryError` with per-attempt detail + soonest cooldown

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["openai/gpt-4o", "openrouter/moonshotai/kimi-k2"],
      },
    },
  },
}
```

Auth state stored in: `~/.openclaw/agents/<agentId>/agent/auth-state.json`  
Auth profiles (keys + OAuth tokens): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`

## Thinking Levels  <!-- sonnet+ -->

Inline directive: `/t <level>` or `/think:<level>` in any message.

| Level | Alias | Notes |
|-------|-------|-------|
| `off` | — | Disabled |
| `minimal` | "think" | |
| `low` | "think hard" | |
| `medium` | "think harder" | |
| `high` | "ultrathink" (max budget) | Also: `highest`, `max` |
| `xhigh` | "ultrathink+" | GPT-5.2 + Codex models only |
| `adaptive` | — | Provider-managed budget (Claude 4.6 default) |

Resolution order: inline directive → session override → per-agent `thinkingDefault` → global default → provider fallback (`adaptive` for Claude 4.6, `low` for other reasoning models, `off` otherwise)

**Session default:** send a message that is ONLY the directive (e.g. `/think:medium`) — it sticks until `/think:off` or session reset.

**Fast mode** (`/fast on|off`): maps to service tier (Anthropic: `auto`/`standard_only`, OpenAI: `service_tier=priority`). Session-pinned, reset by `/fast off`.

**Verbose mode** (`/verbose on|full|off`): exposes tool call summaries as separate bubbles. `full` also forwards tool outputs.

**Reasoning visibility** (`/reasoning on|off|stream`): shows thinking blocks as a separate `Reasoning:` message. `stream` (Telegram only) streams into draft then hides in final reply.

## Bootstrap Files  <!-- sonnet+ -->

All workspace files loaded into system context at session start:

| File | Loaded when | Purpose |
|------|-------------|---------|
| `AGENTS.md` | Every session | Operating instructions + memory rules |
| `SOUL.md` | Every session | Persona, tone, boundaries |
| `USER.md` | Every session | User profile and preferred address |
| `IDENTITY.md` | Every session | Agent name, vibe, emoji |
| `TOOLS.md` | Every session | Local tool conventions (does NOT control availability) |
| `MEMORY.md` | DM sessions only | Long-term durable memory |
| `memory/YYYY-MM-DD.md` | DM sessions | Today + yesterday daily notes |
| `HEARTBEAT.md` | Heartbeat runs | Periodic task checklist |
| `BOOT.md` | Gateway startup | Startup checklist (optional; via boot-md hook) |
| `BOOTSTRAP.md` | First run only | One-time ritual; deleted after completion |
| `DREAMS.md` | Optional | Dream diary (when dreaming enabled) |

**Blank files are skipped.** Large files truncated at `bootstrapMaxChars: 20000` (total: `bootstrapTotalMaxChars: 150000`).

Sub-agents only get: `AGENTS.md` + `TOOLS.md` (no `SOUL.md`, `IDENTITY.md`, `USER.md`, `MEMORY.md`).

## Design Rationale  <!-- opus-only -->

The model selection cascade (4 levels) exists so that:
- Users can override per-session without changing config
- Operators can set per-agent defaults for specialized agents
- A global fallback ensures the system never fails due to missing model config
- A hardcoded fallback is the last resort for unconfigured installations

Pi agent-core was chosen as the execution backend because it handles streaming,
tool loops, and multi-turn conversation natively. OpenClaw wraps it via ACP
to keep the gateway protocol clean and avoid tight coupling.

Auth profile rotation is intentionally session-sticky rather than per-request
to maximize provider cache hit rates. Cooldowns use exponential backoff so
rate-limited providers recover naturally without operator intervention.

## Cross-References  <!-- all-tiers -->

- [[modules/acp.ctx|acp]] — agent spawning protocol
- [[modules/plugins.ctx|plugins]] — skill loading, provider resolution via `PluginRegistry`
- [[modules/config.ctx|config]] — model catalog, auth profiles
- [[modules/channels.ctx|channels]] — chat context (session, transcript)
- [[modules/sessions.ctx|sessions]] — session key, transcript, compaction
- [[modules/hooks.ctx|hooks]] — plugin hooks fire inside agent loop (before_tool_call, before_prompt_build, etc.)
- [[modules/lmstudio.ctx|lmstudio]] — local LLM provider; `normalizeModelRef` routes `lmstudio:` refs here
- [[modules/memory.ctx|memory]] — workspace bootstrap files, pre-compaction memory flush
- Architecture: see [[architecture/AGENT_RUNTIME.ctx|AGENT_RUNTIME]] for workspace layout + 7-stage agent loop
- Architecture: see [[architecture/AGENT_PIPELINE.ctx|AGENT_PIPELINE]] for full pipeline flow
- Architecture: see [[architecture/LOCAL_INFERENCE.ctx|LOCAL_INFERENCE]] for provider routing + fallback cascade
- Architecture: see [[architecture/MULTI_AGENT.ctx|MULTI_AGENT]] for multi-agent routing and sub-agents
