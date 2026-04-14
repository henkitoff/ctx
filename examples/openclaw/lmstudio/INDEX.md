# LM Studio — External Lib Reference

> **LM Studio** is a local LLM inference platform. Runs models on-device.
> Exposes a REST API, native TypeScript/Python SDKs, and OpenAI/Anthropic-compatible endpoints.
>
> Source: https://github.com/lmstudio-ai · Docs: https://lmstudio.ai/docs

This is an **external lib reference** — analogous to `.ctx/ollama/` in large projects.
It documents the LM Studio API surface for agents working on integrations.

---

## Quick Navigation

| Task | Read first |
|------|-----------|
| Integrate LM Studio into a TypeScript project | [[lmstudio/typescript.ctx\|typescript.ctx.md]] |
| Integrate LM Studio into a Python project | [[lmstudio/python.ctx\|python.ctx.md]] |
| Understand available REST endpoints | [[lmstudio/rest-api.ctx\|rest-api.ctx.md]] |
| Use OpenAI/Anthropic client with LM Studio | [[lmstudio/openai-compat.ctx\|openai-compat.ctx.md]] |
| Use `lms` CLI (models, serve, daemon) | [[lmstudio/cli.ctx\|cli.ctx.md]] |
| Understand core concepts (auth, TTL, headless) | [[lmstudio/overview.ctx\|overview.ctx.md]] |

---

## How this lib connects to openclaw

openclaw's `lmstudio` provider plugin (`extensions/lmstudio/`) uses this API:

| openclaw concept | LM Studio surface |
|-----------------|-------------------|
| Provider health check | `GET /api/v1/models` |
| Chat completion | `POST /v1/chat/completions` (OpenAI-compat) |
| Embeddings | `POST /v1/embeddings` |
| Model loading (JIT) | REST model management or SDK |
| Model ref scheme | `lmstudio:<model-id>` |

**Integration context:** [[modules/lmstudio.ctx|openclaw lmstudio integration module]]

---

## API Surface Overview

| Surface | Base URL | Best for |
|---------|----------|---------|
| Native REST v1 | `http://localhost:1234/api/v1/` | Stateful chats, MCP, model management |
| OpenAI-compat | `http://localhost:1234/v1/` | Drop-in replacement for OpenAI clients |
| Anthropic-compat | `http://localhost:1234/v1/messages` | Claude-style message format |
| TypeScript SDK | npm `@lmstudio/sdk` | TypeScript projects, tool calling, plugins |
| Python SDK | pip `lmstudio` | Python projects, data pipelines |
| CLI | `lms` binary | Shell scripts, model management, CI |

**Default port:** 1234 (configurable). All surfaces require LM Studio running.

---

## Critical Invariants

1. **LM Studio must be running** — all API calls fail if the server isn't up
2. **Model must be loaded** — call load or use JIT loading before inference
3. **OpenAI-compat ≠ full parity** — MCP, stateful chats, model mgmt only on native `/api/v1/`
4. **Auth is optional** — token auth available since v0.4.0, disabled by default
5. **Local-only by default** — no data leaves the device; headless mode (`llmster`) for server deployments
