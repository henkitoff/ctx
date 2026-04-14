---
module: architecture/gateway-protocol
type: architecture
purpose: Typed RPC over WebSocket — schema, versioning, client/server contract
affects: [gateway, cli, apps/macos, apps/ios, apps/android, ui]
---

## Overview


The gateway exposes a **typed RPC surface over WebSocket**. All clients (CLI,
macOS/iOS/Android apps, web UI) use the same protocol. Schema is defined once
in `src/gateway/protocol/index.ts` — TypeScript types and AJV runtime validators
are generated from the same source.


## Protocol Invariants


1. Protocol changes are **contract changes** — always version-bump
2. Backward compatibility must be maintained across one major version
3. All params validated with AJV at server entry — before any handler logic
4. All event types are discriminated unions — never open `type: string`


## RPC Methods


| Method | Direction | Purpose |
|--------|-----------|---------|
| `ChatSend` | Client → Server | Send message, get streaming ChatEvents |
| `AgentCommand` | Client → Server | Direct agent invocation with model override |
| `SessionsList` | Client → Server | List active sessions |
| `ChannelsStatus` | Client → Server | Get channel health |
| `GatewayStatus` | Client → Server | Get gateway readiness |
| `ConfigGet` | Client → Server | Read current config |
| `ConfigMutate` | Client → Server | Atomic config mutation |


## Streaming Events


```typescript
// Server → Client: streaming chat response
type ChatEvent =
  | { type: "block";  content: string }           // text chunk
  | { type: "tool";   name: string; args: unknown }// tool call
  | { type: "end";    reason: "stop" | "length" } // clean finish
  | { type: "error";  message: string; code: string }

// Server → Client: agent lifecycle
type AgentEvent =
  | { type: "started";  agentId: string; model: string }
  | { type: "progress"; content: string }
  | { type: "end";      reason: string }
```


## Affected Modules


All clients connect through `gateway/` — it is the single entry point.
