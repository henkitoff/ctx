---
module: lmstudio/typescript
type: external-lib
source: https://github.com/lmstudio-ai/lmstudio-js
provides: [LMStudioClient, llm.model, respond, complete, act, embeddings, model-management]
keywords: [lmstudio-js, typescript, sdk, llm, chat, tools, agent, embeddings]
---

## Purpose  <!-- all-tiers -->

`@lmstudio/sdk` — official TypeScript/JavaScript client for LM Studio.
Works in Node.js and browser. Designed as a cleaner alternative to the OpenAI SDK for local workflows.

```bash
npm install @lmstudio/sdk --save
```

## Public API  <!-- all-tiers -->

| Export / Method | Type | Purpose |
|----------------|------|---------|
| `LMStudioClient` | class | Main entry point — wraps WebSocket connection to LM Studio |
| `client.llm.model(id)` | async fn | Get handle to a loaded (or JIT-loaded) model |
| `model.respond(messages)` | async fn | Chat completion — returns full response |
| `model.respond(messages, {stream})` | async fn | Streaming chat |
| `model.complete(prompt)` | async fn | Text completion |
| `model.act(messages, tools)` | async fn | Autonomous agent loop with tool calling |
| `client.embedding.model(id)` | async fn | Get handle to an embedding model |
| `embModel.embed(text)` | async fn | Generate embeddings |
| `client.llm.load(id, opts)` | async fn | Explicitly load a model with config |
| `client.llm.unload(id)` | async fn | Unload model from memory |
| `client.system.listModels()` | async fn | List downloaded models |
| `client.system.downloadModel(id)` | async fn | Download a model |

## Quick Start  <!-- all-tiers -->

```typescript
import { LMStudioClient } from "@lmstudio/sdk";

const client = new LMStudioClient();
// JIT: model loads automatically if not already loaded
const model = await client.llm.model("qwen/qwen3-4b");
const result = await model.respond("What is the capital of France?");
console.log(result.content);
```

## Chat with History  <!-- all-tiers -->

```typescript
const model = await client.llm.model("qwen/qwen3-4b");
const result = await model.respond([
  { role: "system", content: "You are a helpful assistant." },
  { role: "user",   content: "What is 2 + 2?" },
]);
console.log(result.content); // "4"
```

## Streaming  <!-- sonnet+ -->

```typescript
const model = await client.llm.model("qwen/qwen3-4b");
const stream = model.respond("Tell me a story", { stream: true });
for await (const chunk of stream) {
  process.stdout.write(chunk.content);
}
const finalResult = await stream; // await the stream to get final result
```

## Tool Calling / Autonomous Agents  <!-- sonnet+ -->

```typescript
import { tool } from "@lmstudio/sdk";

const getWeather = tool({
  name: "get_weather",
  description: "Get current weather for a city",
  parameters: {
    city: { type: "string", description: "City name" },
  },
  execute: async ({ city }) => `Sunny, 22°C in ${city}`,
});

const model = await client.llm.model("qwen/qwen3-4b");
const result = await model.act(
  [{ role: "user", content: "What's the weather in Paris?" }],
  [getWeather],
  { onMessage: (msg) => console.log(msg) },
);
console.log(result.content);
```

## Structured Output (JSON Schema)  <!-- sonnet+ -->

```typescript
const result = await model.respond("List 3 European capitals", {
  structured: {
    type: "object",
    properties: {
      capitals: {
        type: "array",
        items: { type: "string" },
      },
    },
  },
});
console.log(JSON.parse(result.content).capitals);
```

## Model Management  <!-- sonnet+ -->

```typescript
// Explicit load with configuration
const model = await client.llm.load("qwen/qwen3-4b", {
  config: {
    contextLength: 8192,
    gpuOffload: "max",
  },
});

// List all downloaded models
const models = await client.system.listModels();
models.forEach(m => console.log(m.modelKey));

// Unload a model from memory
await client.llm.unload("qwen/qwen3-4b");
```

## Embeddings  <!-- sonnet+ -->

```typescript
const embModel = await client.embedding.model("nomic-embed-text");
const vectors = await embModel.embed(["Hello world", "Another text"]);
console.log(vectors[0].length); // e.g. 768
```

## Authentication  <!-- sonnet+ -->

```typescript
const client = new LMStudioClient({
  baseUrl: "http://localhost:1234",
  // token from LM Studio Server Settings
  authToken: process.env.LM_API_TOKEN,
});
```

## Design Notes  <!-- opus-only -->

`lmstudio-js` uses WebSocket under the hood (not HTTP), which enables true streaming without polling and allows stateful model handles. The `LMStudioClient` maintains a persistent connection.

Unlike the OpenAI SDK, `lmstudio-js` exposes:
- `client.llm.load()` with hardware config (GPU offload, context length)
- `client.system.downloadModel()` — programmatic model download
- `model.act()` — a full agent loop, not just single tool-call turns

The Python SDK (`lmstudio-python`) shares the same JSON API schema (generated from `lmstudio-js`).

## Cross-References  <!-- all-tiers -->

- [[lmstudio/overview.ctx|LM Studio Overview]] — auth, headless, TTL, JIT loading
- [[lmstudio/rest-api.ctx|REST API v1]] — underlying HTTP endpoints
- [[lmstudio/openai-compat.ctx|OpenAI compat]] — `/v1/chat/completions` alternative
- [[modules/lmstudio.ctx|openclaw lmstudio integration]] — how openclaw uses this SDK
- [[modules/plugins.ctx|openclaw plugins]] — plugin SDK boundary for provider extensions
