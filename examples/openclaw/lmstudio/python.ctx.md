---
module: lmstudio/python
type: external-lib
source: https://github.com/lmstudio-ai/lmstudio-python
provides: [lms.llm, Chat, complete, respond, act, embeddings, Client, AsyncClient]
keywords: [lmstudio-python, python, sdk, llm, chat, tools, async, scoped]
---

## Purpose  <!-- all-tiers -->

`lmstudio` (pip) — official Python client for LM Studio.
Three API styles for different workflows.

```bash
pip install lmstudio
```

## Three API Styles  <!-- all-tiers -->

| Style | When to use | Entry point |
|-------|-------------|-------------|
| **Convenience** | REPL, notebooks, scripts | `import lmstudio as lms` (implicit client) |
| **Scoped** | Production — deterministic resource cleanup | `with lms.Client() as client:` |
| **Async** | Concurrent pipelines (v1.5.0+) | `async with lms.AsyncClient() as client:` |

## Quick Start (Convenience API)  <!-- all-tiers -->

```python
import lmstudio as lms

# JIT: loads model automatically if not already loaded
model = lms.llm("qwen/qwen3-4b")
result = model.respond("What is the capital of France?")
print(result)  # "Paris"
```

## Chat with History  <!-- all-tiers -->

```python
import lmstudio as lms

model = lms.llm("qwen/qwen3-4b")
chat = lms.Chat("You are a helpful assistant")
chat.add_user_message("What is 2 + 2?")
response = model.respond(chat)
chat.add_assistant_response(response)
print(response)  # "4"
```

## Text Completion  <!-- all-tiers -->

```python
model = lms.llm("qwen/qwen3-4b")
result = model.complete("Once upon a time,")
print(result)
```

## Streaming  <!-- sonnet+ -->

```python
model = lms.llm("qwen/qwen3-4b")
for chunk in model.respond_stream("Tell me a story"):
    print(chunk.content, end="", flush=True)
```

## Tool Calling  <!-- sonnet+ -->

```python
import lmstudio as lms

def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Sunny, 22°C in {city}"

model = lms.llm("qwen/qwen3-4b")
chat = lms.Chat()
chat.add_user_message("What's the weather in Paris?")
result = model.act(chat, tools=[get_weather])
print(result)
```

Python docstrings are used as tool descriptions — no schema boilerplate needed.

## Structured Output  <!-- sonnet+ -->

```python
from pydantic import BaseModel

class Capitals(BaseModel):
    cities: list[str]

model = lms.llm("qwen/qwen3-4b")
result = model.respond("List 3 European capitals", response_format=Capitals)
print(result.cities)
```

## Scoped API (production)  <!-- sonnet+ -->

```python
import lmstudio as lms

with lms.Client() as client:
    model = client.llm.model("qwen/qwen3-4b")
    result = model.respond("Hello")
    print(result)
# connection and resources cleaned up on exit
```

## Async API (v1.5.0+)  <!-- sonnet+ -->

```python
import asyncio
import lmstudio as lms

async def main():
    async with lms.AsyncClient() as client:
        model = await client.llm.model("qwen/qwen3-4b")
        result = await model.respond("Hello async")
        print(result)

asyncio.run(main())
```

**Timeout config (sync API):**
```python
lms.set_sync_api_timeout(120)  # default: 60s inactivity timeout
```

## Embeddings  <!-- sonnet+ -->

```python
embed_model = lms.embedding_model("nomic-embed-text")
vectors = embed_model.embed(["Hello world", "Another sentence"])
print(len(vectors[0]))  # e.g. 768
```

## Model Management  <!-- sonnet+ -->

```python
# List downloaded models
for model in lms.list_models():
    print(model.model_key)

# Explicitly load with config
model = lms.llm("qwen/qwen3-4b", config={"contextLength": 8192})

# Download a model
lms.download_model("qwen/qwen3-4b")

# Unload
lms.unload("qwen/qwen3-4b")
```

## Authentication  <!-- sonnet+ -->

```python
with lms.Client(base_url="http://localhost:1234", auth_token="your-token") as client:
    model = client.llm.model("qwen/qwen3-4b")
```

## Design Notes  <!-- opus-only -->

The Python SDK's JSON API schema is automatically generated from `lmstudio-js` (via `tox -e sync-sdk-schema`). This ensures both SDKs always expose identical semantics.

The convenience API (`import lmstudio as lms`) uses a module-level implicit `Client` that persists until the interpreter exits — fine for scripts, problematic for long-running services where explicit lifecycle management via the scoped API is preferred.

## Cross-References  <!-- all-tiers -->

- [[lmstudio/overview.ctx|LM Studio Overview]] — auth, headless, TTL, JIT loading
- [[lmstudio/typescript.ctx|TypeScript SDK]] — JS equivalent with same API shape
- [[lmstudio/rest-api.ctx|REST API v1]] — underlying HTTP endpoints
- [[modules/lmstudio.ctx|openclaw lmstudio integration]] — provider plugin context
