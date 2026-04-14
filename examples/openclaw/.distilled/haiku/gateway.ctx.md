---
module: modules/gateway
type: codebase
depends_on: [config, plugins, channels, agents, sessions, infra, security]
depended_by: [cli, commands]
provides: [GatewayServer, attachGatewayWsConnectionHandler, ChatSendParams, ChatEvent, AgentEvent]
invariants:
  - "Protocol changes are contract changes — require versioning"
  - "RPC handlers live in src/gateway/server-methods/ only"
  - "WS auth validated on every connection, not just handshake"
keywords: [gateway, websocket, rpc, protocol, server, control-plane]
---

## Purpose


The `gateway` module is the **WebSocket control plane** connecting all clients
(CLI, macOS/iOS/Android apps, web UI) to the OpenClaw core. It exposes a typed
RPC surface over WebSocket and handles auth, connection lifecycle, and plugin
HTTP routes.

Key components:
- **`server/`** — HTTP/WS server, connection handling, TLS, auth
- **`protocol/`** — Typed RPC schema (ChatSend, AgentCommand, SessionsList, …)
- **`server-methods/`** — RPC handler implementations
- **`ws-connection/`** — WebSocket lifecycle, auth, flood guards
- **`plugins-http.ts`** — Plugin HTTP route dispatch


## Public API


| Export | Type | Purpose |
|--------|------|---------|
| `ChatSendParams` | type | Inbound chat send request |
| `ChatEvent` | type | Streaming response from chat (block/tool/end) |
| `AgentEvent` | type | Agent execution lifecycle events |
| `AgentIdentityParams` | type | Agent identity + model override per call |
| `SessionsListParams` | type | List sessions request |
| `attachGatewayWsConnectionHandler` | fn | Bind WS handler to HTTP server |
| `validateChatSendParams` | fn | AJV-compiled RPC schema validator |


## Invariants


1. Protocol changes are **contract changes** — bump version, maintain backward compat
2. All RPC handlers implemented in `src/gateway/server-methods/` — never inline
3. WS auth validated on **every connection**, not just initial handshake
4. Gateway never calls channel adapters directly — routes via `channels/` module
5. **First WebSocket frame must be `connect`** — non-connect or non-JSON frames → hard close
6. Gateway refuses to bind on non-loopback without valid auth config — **fail-fast by design**
7. OpenAI-compatible API exposes agents as models — `openclaw/default` is the stable alias


## Cross-References


- `agents/` — gateway calls `agentCommand()` for agent execution
- `channels/` — gateway dispatches inbound messages to channel adapters
- `config/` — loads gateway config (port, TLS, auth mode)
- Architecture: see architecture/GATEWAY_PROTOCOL.ctx.md for full RPC design
