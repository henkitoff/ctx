---
module: lmstudio/openai-compat
type: external-lib
source: https://lmstudio.ai/docs/developer
provides: [/v1/chat/completions, /v1/completions, /v1/embeddings, /v1/responses, /v1/messages]
keywords: [openai, anthropic, compatibility, drop-in, chat/completions, streaming, tools]
---

## Purpose  <!-- all-tiers -->

LM Studio exposes OpenAI-compatible and Anthropic-compatible endpoints.
Drop-in replacement: point existing OpenAI/Anthropic clients at `http://localhost:1234`.

**Use this for:** existing code that uses the OpenAI SDK, Anthropic SDK, or any OpenAI-compat client.
**Use `/api/v1/` instead for:** stateful chats, MCP, model management, download.

## OpenAI-Compatible Endpoints  <!-- all-tiers -->

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET`  | `/v1/models` | List loaded models |
| `POST` | `/v1/chat/completions` | Chat completion (streaming or not) |
| `POST` | `/v1/completions` | Text completion |
| `POST` | `/v1/embeddings` | Text embeddings |
| `POST` | `/v1/responses` | Stateful chat (OpenAI Responses API style) |

## Quick Start — OpenAI SDK  <!-- all-tiers -->

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "http://localhost:1234/v1",
  apiKey: "lm-studio",  // any non-empty string works unless auth is enabled
});

const response = await client.chat.completions.create({
  model: "qwen/qwen3-4b",
  messages: [{ role: "user", content: "Hello!" }],
});
console.log(response.choices[0].message.content);
```

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
response = client.chat.completions.create(
    model="qwen/qwen3-4b",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

## Chat Completions  <!-- all-tiers -->

```bash
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3-4b",
    "messages": [
      {"role": "system", "content": "You are helpful."},
      {"role": "user", "content": "What is 2+2?"}
    ],
    "stream": false
  }'
```

## Streaming  <!-- sonnet+ -->

```bash
curl http://localhost:1234/v1/chat/completions \
  -d '{"model": "qwen/qwen3-4b", "messages": [...], "stream": true}'
```

Returns SSE (Server-Sent Events):
```
data: {"choices": [{"delta": {"content": "4"}}]}
data: [DONE]
```

## Tool Calling  <!-- sonnet+ -->

```json
{
  "model": "qwen/qwen3-4b",
  "messages": [{"role": "user", "content": "What's the weather in Paris?"}],
  "tools": [{
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Get current weather",
      "parameters": {
        "type": "object",
        "properties": {
          "city": {"type": "string"}
        },
        "required": ["city"]
      }
    }
  }],
  "tool_choice": "auto"
}
```

## Structured Output (JSON Schema)  <!-- sonnet+ -->

```json
{
  "model": "qwen/qwen3-4b",
  "messages": [{"role": "user", "content": "List 3 capitals"}],
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "capitals",
      "schema": {
        "type": "object",
        "properties": {
          "cities": {"type": "array", "items": {"type": "string"}}
        }
      }
    }
  }
}
```

## Anthropic-Compatible Endpoint  <!-- sonnet+ -->

```bash
curl http://localhost:1234/v1/messages \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "qwen/qwen3-4b",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello, Claude!"}]
  }'
```

Works with the Anthropic Python/TypeScript SDK pointed at `http://localhost:1234`.
Also enables **Claude Code** to use local models via `ANTHROPIC_BASE_URL=http://localhost:1234`.

## Authentication  <!-- sonnet+ -->

```bash
# OpenAI-compat: Authorization Bearer
curl -H "Authorization: Bearer $LM_API_TOKEN" http://localhost:1234/v1/chat/completions ...

# Anthropic-compat: x-api-key header
curl -H "x-api-key: $LM_API_TOKEN" http://localhost:1234/v1/messages ...
```

## Embeddings  <!-- sonnet+ -->

```bash
curl http://localhost:1234/v1/embeddings \
  -d '{
    "model": "nomic-embed-text",
    "input": ["Hello world", "Another sentence"]
  }'
```

## Limitations vs Native API  <!-- opus-only -->

The OpenAI-compat surface does NOT expose:
- Stateful chat with `response_id` (use `/api/v1/chat` for that)
- Model load/unload/download management (use `/api/v1/load` etc.)
- MCP server integration (use `/api/v1/chat` with `tools: [{type: "mcp"}]`)
- Tokenize endpoint

For full LM Studio feature access, use the native `/api/v1/` endpoints or the TypeScript/Python SDKs.

## Cross-References  <!-- all-tiers -->

- [[lmstudio/rest-api.ctx|REST API v1]] — native endpoints with full feature access
- [[lmstudio/overview.ctx|LM Studio Overview]] — auth, server setup
- [[lmstudio/typescript.ctx|TypeScript SDK]] — recommended for TypeScript projects
- [[modules/lmstudio.ctx|openclaw lmstudio integration]] — openclaw uses `/v1/chat/completions` for inference
