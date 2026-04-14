---
module: lmstudio/rest-api
type: external-lib
source: https://lmstudio.ai/docs/developer
provides: [/api/v1/chat, /api/v1/load, /api/v1/unload, /api/v1/models, /api/v1/tokenize, /api/v1/download]
keywords: [rest, http, api, v1, stateful-chat, model-management, mcp, tokenize]
---

## Purpose  <!-- all-tiers -->

LM Studio native REST API — more capable than OpenAI-compat for local workflows.
Base URL: `http://localhost:1234/api/v1/`

**Use this (not OpenAI-compat) for:** stateful chats, MCP, model load/unload, download, tokenization.

## Endpoint Map  <!-- all-tiers -->

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET`  | `/api/v1/models` | List loaded models |
| `POST` | `/api/v1/chat` | Stateful chat (persists history server-side) |
| `POST` | `/api/v1/load` | Load a model into memory |
| `POST` | `/api/v1/unload` | Unload a model |
| `POST` | `/api/v1/download` | Download a model from Hub |
| `POST` | `/api/v1/tokenize` | Count tokens for a prompt |

## List Models  <!-- all-tiers -->

```bash
curl http://localhost:1234/api/v1/models
```

```json
{
  "data": [
    { "id": "qwen/qwen3-4b", "state": "loaded", "maxContextLength": 32768 }
  ]
}
```

## Stateful Chat  <!-- all-tiers -->

```bash
# First turn — server creates a session, returns response_id
curl -X POST http://localhost:1234/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3-4b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

```json
{
  "id": "chat-abc123",
  "choices": [{ "message": { "role": "assistant", "content": "Hi there!" } }]
}
```

```bash
# Continue the conversation — pass response_id to maintain history
curl -X POST http://localhost:1234/api/v1/chat \
  -d '{"model": "qwen/qwen3-4b", "messages": [...], "response_id": "chat-abc123"}'
```

**Stateful = history is stored server-side.** No need to resend the full transcript.

## Load Model  <!-- sonnet+ -->

```bash
curl -X POST http://localhost:1234/api/v1/load \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3-4b",
    "config": {
      "contextLength": 8192,
      "gpuOffload": "max"
    }
  }'
```

`gpuOffload`: `"max"` | `"auto"` | `0..1` (fraction) | integer (layers)

## Unload Model  <!-- sonnet+ -->

```bash
curl -X POST http://localhost:1234/api/v1/unload \
  -d '{"model": "qwen/qwen3-4b"}'
```

## Download Model  <!-- sonnet+ -->

```bash
curl -X POST http://localhost:1234/api/v1/download \
  -d '{
    "model": "qwen/qwen3-4b-2507",
    "quantization": "Q4_K_M"
  }'
```

Returns a stream of download progress events (NDJSON).

## Tokenize  <!-- sonnet+ -->

```bash
curl -X POST http://localhost:1234/api/v1/tokenize \
  -d '{
    "model": "qwen/qwen3-4b",
    "text": "Hello, how many tokens am I?"
  }'
```

```json
{ "token_count": 8, "tokens": [9906, 11, 1246, 1239, ...] }
```

## Authentication  <!-- sonnet+ -->

When Server Authentication is enabled:
```bash
curl -H "Authorization: Bearer $LM_API_TOKEN" http://localhost:1234/api/v1/models
```

## MCP via API  <!-- sonnet+ -->

Run MCP tools server-side by referencing them in the chat request:
```json
{
  "model": "qwen/qwen3-4b",
  "messages": [{"role": "user", "content": "Search the web for X"}],
  "tools": [{"type": "mcp", "server": "brave-search"}]
}
```

MCP servers can be ephemeral (started per-request) or persistent (configured in `mcp.json`).

## Streaming  <!-- sonnet+ -->

All chat endpoints support streaming via `"stream": true`. Returns NDJSON:
```
data: {"choices": [{"delta": {"content": "Hello"}}], "done": false}
data: {"choices": [{"delta": {"content": " there"}}], "done": false}
data: [DONE]
```

## Cross-References  <!-- all-tiers -->

- [[lmstudio/overview.ctx|LM Studio Overview]] — server setup, auth, TTL
- [[lmstudio/openai-compat.ctx|OpenAI/Anthropic compat]] — `/v1/` endpoints for drop-in clients
- [[lmstudio/typescript.ctx|TypeScript SDK]] — SDK abstraction over this API
- [[lmstudio/python.ctx|Python SDK]] — Python abstraction over this API
- [[modules/lmstudio.ctx|openclaw lmstudio integration]] — openclaw uses `/api/v1/models` for health check
