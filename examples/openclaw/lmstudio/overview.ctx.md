---
module: lmstudio/overview
type: external-lib
source: https://lmstudio.ai/docs
provides: [LMStudioClient, lms.llm, REST-v1, OpenAI-compat, Anthropic-compat]
keywords: [lmstudio, local-llm, inference, server, auth, headless, ttl, jit]
---

## Purpose  <!-- all-tiers -->

LM Studio is a local LLM inference platform. Runs models on-device, exposes multiple API surfaces.

**Server:** default `http://localhost:1234` (configurable). Must be running before any API call.

**API surfaces:**

| Surface | Base URL | Notes |
|---------|----------|-------|
| Native REST v1 | `/api/v1/` | Stateful chats, MCP, model management |
| OpenAI-compat | `/v1/` | Drop-in for OpenAI clients |
| Anthropic-compat | `/v1/messages` | Claude-style message format |
| TypeScript SDK | `@lmstudio/sdk` | npm, JIT load, tool calling |
| Python SDK | `lmstudio` (pip) | 3 styles: convenience / scoped / async |
| CLI | `lms` | Model management, serve, daemon |

## Authentication  <!-- all-tiers -->

Optional — disabled by default. Enable in Server Settings → "Require Authentication".

```bash
# Bearer token for REST + OpenAI-compat
Authorization: Bearer $LM_API_TOKEN

# Anthropic-compat header
x-api-key: $LM_API_TOKEN
```

Tokens are created in the LM Studio Server Settings panel. Each token can have scoped permissions.

## Model Loading  <!-- all-tiers -->

Models must be loaded before inference. Three approaches:

| Approach | How | When |
|----------|-----|------|
| Pre-load | Load via UI or `/api/v1/load` | Persistent sessions |
| JIT (Just-In-Time) | SDK auto-loads on first call | Dev / short-lived |
| CLI | `lms load <model-id>` | Scripts / CI |

**JIT load:** SDK loads model automatically if not already loaded. Adds latency to first call.

## TTL and Auto-Eviction  <!-- sonnet+ -->

Models consume VRAM. Configure idle eviction to free memory automatically.

```bash
# Per-request TTL via API header
X-LM-Studio-TTL: 300   # seconds; model unloads after 300s idle

# Or set server-wide default in Server Settings → TTL
```

Eviction is model-scoped, not session-scoped. A model used by multiple sessions stays loaded until all sessions are idle past the TTL.

## Headless Deployment  <!-- sonnet+ -->

Two headless modes:

**1. Desktop app as background service:**
```bash
# Enable in: LM Studio → Settings → Enable as background service
# API is then available without the UI open
```

**2. `llmster` daemon (Linux/Mac, production):**
```bash
# Install
curl -fsSL https://files.lmstudio.ai/llmster/install.sh | bash

# Run
llmster --port 1234

# As systemd service
llmster install-service && systemctl enable --now llmster
```

`llmster` = LM Studio's inference core, packaged as a standalone daemon for servers and CI.

## Cross-References  <!-- all-tiers -->

- [[lmstudio/typescript.ctx|TypeScript SDK]] — `@lmstudio/sdk` full reference
- [[lmstudio/python.ctx|Python SDK]] — `lmstudio` pip package reference
- [[lmstudio/rest-api.ctx|REST API v1]] — native endpoints reference
- [[lmstudio/openai-compat.ctx|OpenAI/Anthropic compat]] — drop-in compatibility
- [[lmstudio/cli.ctx|CLI]] — `lms` command reference
- [[modules/lmstudio.ctx|openclaw lmstudio integration]] — how openclaw uses this API
