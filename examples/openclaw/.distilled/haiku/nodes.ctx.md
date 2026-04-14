---
module: modules/nodes
type: codebase
depends_on: [gateway, config, infra]
depended_by: [agents, gateway, channels]
provides: [NodeHost, NodeCapabilities, NodeStatus, approveNode, invokeNode]
invariants:
  - "Node devices connect via WebSocket with role:node — same WS endpoint as clients"
  - "All node connects require pairing approval — even loopback node connections"
  - "Node capabilities are declared on connect — agents must not assume a capability exists"
keywords: [nodes, devices, paired, ios, android, camera, screen, canvas, location, headless]

tags: [ctx/module]
---

## Purpose


The `nodes` module manages **paired devices** — macOS, iOS, Android, and headless
machines that connect to the Gateway and expose hardware capabilities to agents.
Nodes extend what agents can do beyond text: take photos, capture screens, get
GPS location, or drive a remote Canvas UI.

Key components:
- **`node-host/`** — Runs on the paired device; declares capabilities; receives invocations
- **`node-registry/`** — Gateway-side registry of connected nodes and their capabilities
- **`node-methods/`** — RPC handlers for node invocations (camera, canvas, screen, location)
- **`pairing/`** — Device identity, challenge/response, approval flow


## Public API


| Export | Type | Purpose |
|--------|------|---------|
| `NodeHost` | class | Runs on the device — connects to Gateway with `role: node` |
| `NodeCapabilities` | type | Declared capabilities: camera, screen, canvas, location, voice |
| `NodeStatus` | type | Connection state + last-seen + capability summary |
| `approveNode` | fn | Approve a pending device pairing request |
| `invokeNode` | fn | Send invocation to a paired node (camera shot, canvas render, …) |
| `listNodes` | fn | List all connected/known nodes with status |


## Invariants


1. Node devices use the **same WS endpoint** as control clients, with `role: node` in connect frame
2. All node connects require **explicit pairing approval** — even same-host loopback
3. Node capabilities are **declared on connect** — agents query before invoking; never assume
4. Invocations are **one-shot RPC** — no persistent streaming channel between agent and node


## Cross-References


- [[modules/gateway.ctx|gateway]] — node WS connections handled by same gateway server; RPC handlers in gateway/server-methods
- [[modules/agents.ctx|agents]] — `nodes` built-in tool lets agents invoke paired devices
- [[modules/config.ctx|config]] — gateway bind/auth config affects node reachability
- [[modules/infra.ctx|infra]] — TLS, port availability for gateway that nodes connect to
