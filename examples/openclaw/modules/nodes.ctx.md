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

## Purpose  <!-- all-tiers -->

The `nodes` module manages **paired devices** — macOS, iOS, Android, and headless
machines that connect to the Gateway and expose hardware capabilities to agents.
Nodes extend what agents can do beyond text: take photos, capture screens, get
GPS location, or drive a remote Canvas UI.

Key components:
- **`node-host/`** — Runs on the paired device; declares capabilities; receives invocations
- **`node-registry/`** — Gateway-side registry of connected nodes and their capabilities
- **`node-methods/`** — RPC handlers for node invocations (camera, canvas, screen, location)
- **`pairing/`** — Device identity, challenge/response, approval flow

## Public API  <!-- all-tiers -->

| Export | Type | Purpose |
|--------|------|---------|
| `NodeHost` | class | Runs on the device — connects to Gateway with `role: node` |
| `NodeCapabilities` | type | Declared capabilities: camera, screen, canvas, location, voice |
| `NodeStatus` | type | Connection state + last-seen + capability summary |
| `approveNode` | fn | Approve a pending device pairing request |
| `invokeNode` | fn | Send invocation to a paired node (camera shot, canvas render, …) |
| `listNodes` | fn | List all connected/known nodes with status |

## Invariants  <!-- all-tiers -->

1. Node devices use the **same WS endpoint** as control clients, with `role: node` in connect frame
2. All node connects require **explicit pairing approval** — even same-host loopback
3. Node capabilities are **declared on connect** — agents query before invoking; never assume
4. Invocations are **one-shot RPC** — no persistent streaming channel between agent and node

## Key Patterns  <!-- sonnet+ -->

**Node connect frame:**
```json
{
  "type": "connect",
  "params": {
    "role": "node",
    "deviceId": "iphone-se-xyz",
    "auth": { "token": "<pairing-token>" },
    "capabilities": ["camera", "location", "canvas"],
    "platform": "ios",
    "deviceFamily": "mobile"
  }
}
```

**Agent invoking a node:**
```typescript
// Via the `nodes` built-in tool
nodes({ action: "camera", deviceId: "iphone-se-xyz", options: { flash: false } })
→ { ok: true, mediaRef: "media://session/xyz/camera-001.jpg" }

nodes({ action: "location", deviceId: "iphone-se-xyz" })
→ { ok: true, coords: { lat: 48.137, lon: 11.576, accuracy: 5 } }
```

**Pairing approval flow:**
```bash
# On gateway host — approve a pending device
openclaw nodes pending          # list devices awaiting approval
openclaw nodes approve <id>     # approve
openclaw nodes reject <id>      # reject

# Generate QR for mobile setup
openclaw qr                     # prints pairing QR to terminal
```

**Node lifecycle:**
```bash
# On the headless node device
openclaw node run               # start node process, connect to gateway
openclaw node install           # install as launchd/systemd service
openclaw node status            # check connection state

# From gateway host
openclaw nodes status           # all connected nodes
openclaw nodes describe <id>    # details, capabilities, last invocation
openclaw nodes invoke <id> camera --json   # trigger camera, get result
openclaw nodes canvas <id> --html "..."    # push HTML to node Canvas
openclaw nodes screen <id>      # capture screenshot from node
```

## Internal Structure  <!-- sonnet+ -->

```
src/nodes/
├── node-host/
│   ├── index.ts            ← NodeHost class (runs on device)
│   ├── capabilities.ts     ← Declare + advertise capabilities
│   └── handlers/
│       ├── camera.ts       ← Handle camera invocation
│       ├── screen.ts       ← Handle screen capture
│       ├── canvas.ts       ← Handle canvas render/eval
│       └── location.ts     ← Handle GPS request
├── node-registry/
│   ├── index.ts            ← Gateway-side registry
│   ├── status.ts           ← NodeStatus tracking
│   └── invocations.ts      ← Route invocations to connected nodes
├── pairing/
│   ├── approval.ts         ← Approve/reject pending devices
│   ├── challenge.ts        ← Challenge/response signing
│   └── device-token.ts     ← Issue + rotate pairing tokens
└── rpc-methods/
    ├── nodes-list.ts       ← listNodes RPC handler
    ├── nodes-invoke.ts     ← invokeNode RPC handler
    └── nodes-approve.ts    ← approveNode RPC handler
```

## Design Rationale  <!-- opus-only -->

**Why same WS endpoint for nodes and clients?**
A single port multiplexes all connection types. The `role` field in the connect
frame disambiguates. This eliminates a second port to manage and firewall, and
ensures nodes benefit from the same auth, pairing, and TLS machinery as clients.

**Why explicit pairing for loopback nodes?**
Loopback control clients (CLI, web UI) are auto-approved because they are assumed
to be operated by the Gateway owner. Nodes, however, are separate devices that may
be shared or misconfigured. Explicit pairing ensures the operator consciously
approves what hardware capability they're exposing to agents.

**Why one-shot RPC instead of streaming?**
Node invocations are discrete events (take a photo, get location). A persistent
streaming channel would require nodes to maintain long-lived connections even when
idle, increasing resource cost on mobile devices. One-shot RPC is connection-efficient
and maps cleanly to the underlying native APIs (camera capture, GPS fix).

## Cross-References  <!-- all-tiers -->

- [[modules/gateway.ctx|gateway]] — node WS connections handled by same gateway server; RPC handlers in gateway/server-methods
- [[modules/agents.ctx|agents]] — `nodes` built-in tool lets agents invoke paired devices
- [[modules/config.ctx|config]] — gateway bind/auth config affects node reachability
- [[modules/infra.ctx|infra]] — TLS, port availability for gateway that nodes connect to
