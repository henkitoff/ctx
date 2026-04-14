---
module: modules/acp
type: codebase
depends_on: [gateway, config]
depended_by: [agents]
provides: [AcpServer, AcpSession, AcpServerOptions]
invariants:
  - "ACP is the only way agents communicate back to the gateway — no direct calls"
  - "ACP session lifetime matches agent invocation lifetime"
keywords: [acp, agent-client-protocol, protocol, session, events, pi-agent]
---

## Purpose  <!-- all-tiers -->

The `acp` module implements the **Agent Client Protocol**: the wire format over
which the Pi agent-core communicates with OpenClaw's gateway during execution.

ACP sits between the agent runtime and the gateway RPC layer, translating
Pi agent events (blocks, tool calls, errors) into OpenClaw `ChatEvent` / `AgentEvent`
types that clients receive over WebSocket.

Key components:
- **`server.ts`** — ACP server (listens for Pi agent output)
- **`client.ts`** — ACP client (used by Pi agent to send events)
- **`session.ts`** — ACP session lifecycle
- **`event-mapper.ts`** — Pi events ↔ OpenClaw events translation
- **`translator.ts`** — Error/prompt handling translation

## Public API  <!-- all-tiers -->

| Export | Type | Purpose |
|--------|------|---------|
| `AcpServer` | class | Start ACP server for Pi agent to connect |
| `AcpSession` | type | Active agent session handle |
| `AcpServerOptions` | type | Server config (port, timeout, auth) |

## Invariants  <!-- all-tiers -->

1. ACP is the **only** communication channel between agent and gateway — no direct calls
2. ACP session lifetime = agent invocation lifetime — closed on agent exit
3. Events are ordered and delivered in-sequence — no out-of-order delivery

## Key Patterns  <!-- sonnet+ -->

**ACP data flow:**
```
Pi agent-core (runs agent loop)
  ↓ ACP events (HTTP or unix socket)
AcpServer (src/acp/server.ts)
  ↓ event-mapper.ts
ChatEvent / AgentEvent
  ↓ gateway/server-methods
WebSocket → Client (CLI/App)
```

**Event translation:**
```typescript
// Pi agent emits:
{ type: "content_block", text: "Hello" }

// ACP maps to OpenClaw ChatEvent:
{ type: "block", content: "Hello" }

// Pi agent tool call:
{ type: "tool_use", name: "browser", input: { url: "..." } }

// ACP maps to:
{ type: "tool", name: "browser", args: { url: "..." } }
```

## Design Rationale  <!-- opus-only -->

ACP (Agent Client Protocol) decouples the agent execution engine from the
gateway's RPC protocol. This means OpenClaw can upgrade either side
independently — e.g., swap Pi agent-core version or change the gateway
WebSocket protocol without touching both at once.

The translation layer (`event-mapper.ts`) also normalizes provider-specific
streaming differences (Anthropic vs OpenAI streaming formats) into a single
OpenClaw event vocabulary.

## Cross-References  <!-- all-tiers -->

- [[modules/agents.ctx|agents]] — spawns Pi agent via ACP (`acp-spawn.ts`)
- [[modules/gateway.ctx|gateway]] — `ChatEvent` / `AgentEvent` types consumed by clients
- [[modules/config.ctx|config]] — ACP session config (port, timeout)
- Architecture: [[architecture/AGENT_PIPELINE.ctx|AGENT_PIPELINE]] — full execution flow
