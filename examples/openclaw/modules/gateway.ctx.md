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

## Purpose  <!-- all-tiers -->

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

## Public API  <!-- all-tiers -->

| Export | Type | Purpose |
|--------|------|---------|
| `ChatSendParams` | type | Inbound chat send request |
| `ChatEvent` | type | Streaming response from chat (block/tool/end) |
| `AgentEvent` | type | Agent execution lifecycle events |
| `AgentIdentityParams` | type | Agent identity + model override per call |
| `SessionsListParams` | type | List sessions request |
| `attachGatewayWsConnectionHandler` | fn | Bind WS handler to HTTP server |
| `validateChatSendParams` | fn | AJV-compiled RPC schema validator |

## Invariants  <!-- all-tiers -->

1. Protocol changes are **contract changes** — bump version, maintain backward compat
2. All RPC handlers implemented in `src/gateway/server-methods/` — never inline
3. WS auth validated on **every connection**, not just initial handshake
4. Gateway never calls channel adapters directly — routes via `channels/` module
5. **First WebSocket frame must be `connect`** — non-connect or non-JSON frames → hard close
6. Gateway refuses to bind on non-loopback without valid auth config — **fail-fast by design**
7. OpenAI-compatible API exposes agents as models — `openclaw/default` is the stable alias

## Key Patterns  <!-- sonnet+ -->

**WebSocket frame protocol:**
```json
// Client → Gateway (request)
{ "type": "req", "id": "r1", "method": "chat.send", "params": { ... } }

// Gateway → Client (response)
{ "type": "res", "id": "r1", "ok": true, "payload": { ... } }

// Gateway → Client (event, no id)
{ "type": "event", "event": "agent", "payload": { ... }, "seq": 42, "stateVersion": 7 }
```

Mandatory handshake: first frame is `connect`; gateway responds with `hello-ok`
containing presence, health, state version, uptime, policy limits, and available methods.
Non-JSON or non-connect first frames → **immediate hard close**.

**Auth modes:**
```json5
// Shared secret (default)
{ "gateway": { "auth": { "token": "my-secret" } } }

// Tailscale identity (no token needed over Tailnet)
{ "gateway": { "auth": { "allowTailscale": true } } }

// Trusted-proxy (reverse proxy sets identity headers)
{ "gateway": { "auth": { "mode": "trusted-proxy" } } }

// No auth — loopback only, development only
{ "gateway": { "auth": { "mode": "none" } } }
```

**OpenAI-compatible API (same port as WS):**
```
GET  /v1/models                 → lists agents as models
GET  /v1/models/{id}            → single model/agent info
POST /v1/chat/completions       → agent run (streaming SSE)
POST /v1/responses              → OpenAI Responses API format
POST /v1/embeddings             → embedding via configured provider
```
Agent IDs as model names: `openclaw`, `openclaw/default`, `openclaw/<agentId>`.
Override with `x-openclaw-model` header for provider/model passthrough.

**Canvas & A2UI HTTP endpoints:**
```
/__openclaw__/canvas/           ← agent-editable HTML/CSS/JS (A2Canvas)
/__openclaw__/a2ui/             ← A2UI host for node Canvas
```
Both served on the same port (default 18789).

**Port and bind resolution order:**
1. CLI `--port` flag
2. `OPENCLAW_GATEWAY_PORT` env var
3. `gateway.port` in config
4. Default: `18789`

Bind: loopback only by default. Non-loopback requires explicit `gateway.bind` config
AND valid auth — gateway fails fast without both.

**Hot reload modes:**
| Mode | Behavior |
|------|----------|
| `off` | Disabled |
| `hot` | Apply safe config changes without restart |
| `restart` | Full restart for incompatible changes |
| `hybrid` | Apply safely, restart when needed (default) |

**Common failure signatures:**
```
"refusing to bind gateway ... without auth"     → non-loopback + no auth config
"another gateway instance already listening"    → EADDRINUSE / port conflict
"Gateway start blocked: set gateway.mode=local" → config mode mismatch
"unauthorized" during connect                   → auth token mismatch
"first frame must be connect"                   → client protocol violation
```

**Plugin HTTP routes:**
Plugins can register custom HTTP routes via `gateway` adapter in their manifest.
The gateway dispatches to `src/gateway/plugins-http.ts`.

## Internal Structure  <!-- sonnet+ -->

```
src/gateway/
├── server/
│   ├── index.ts              ← GatewayServer entry
│   ├── ws-connection.ts      ← WebSocket lifecycle
│   ├── http-listen.ts        ← HTTP server + TLS setup
│   └── auth.ts               ← Token validation
├── protocol/
│   └── index.ts              ← Full typed RPC schema (AJV schemas + TS types)
├── server-methods/
│   ├── chat-send.ts          ← Handle ChatSend RPC
│   ├── agent-command.ts      ← Handle AgentCommand RPC
│   └── sessions-list.ts      ← Handle SessionsList RPC
└── plugins-http.ts           ← Plugin route dispatch
```

## Design Rationale  <!-- opus-only -->

WebSocket was chosen over HTTP polling because agent responses are streaming
(token-by-token) and multiple concurrent sessions need push delivery without
polling overhead. The typed RPC schema (AJV at runtime + TypeScript types
generated from the same source) ensures clients and server stay in sync.

The flood guard exists because agents can be slow (multi-second responses) and
a fast client could queue many requests that overwhelm memory.

## Cross-References  <!-- all-tiers -->

- [[modules/agents.ctx|agents]] — gateway calls `agentCommand()` for agent execution
- [[modules/channels.ctx|channels]] — gateway dispatches inbound messages to channel adapters
- [[modules/config.ctx|config]] — loads gateway config (port, TLS, auth mode)
- [[modules/plugins.ctx|plugins]] — plugin HTTP route dispatch
- [[modules/sessions.ctx|sessions]] — session key routing per connection
- [[modules/infra.ctx|infra]] — port availability and TLS setup
- [[modules/acp.ctx|acp]] — agent events flow from ACP → gateway protocol
- Architecture: [[architecture/GATEWAY_PROTOCOL.ctx|GATEWAY_PROTOCOL]] — full RPC design
