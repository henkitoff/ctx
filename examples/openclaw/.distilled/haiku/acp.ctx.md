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

## Purpose


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


## Public API


| Export | Type | Purpose |
|--------|------|---------|
| `AcpServer` | class | Start ACP server for Pi agent to connect |
| `AcpSession` | type | Active agent session handle |
| `AcpServerOptions` | type | Server config (port, timeout, auth) |


## Invariants


1. ACP is the **only** communication channel between agent and gateway — no direct calls
2. ACP session lifetime = agent invocation lifetime — closed on agent exit
3. Events are ordered and delivered in-sequence — no out-of-order delivery


## Cross-References


- `agents/` — spawns Pi agent via ACP (`acp-spawn.ts`)
- `gateway/protocol/` — `ChatEvent` / `AgentEvent` types consumed by clients
- Architecture: see architecture/AGENT_PIPELINE.ctx.md for full execution flow
