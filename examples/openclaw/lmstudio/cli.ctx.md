---
module: lmstudio/cli
type: external-lib
source: https://github.com/lmstudio-ai/lms
provides: [lms-load, lms-ls, lms-get, lms-serve, lms-daemon, lms-ps, lms-unload]
keywords: [lms, cli, models, serve, daemon, download, management]
---

## Purpose  <!-- all-tiers -->

`lms` — LM Studio command-line tool for model management and server control.

```bash
# Install (if not already bundled with LM Studio)
curl -fsSL https://files.lmstudio.ai/lms/install.sh | bash
```

## Commands  <!-- all-tiers -->

| Command | Purpose |
|---------|---------|
| `lms ls` | List downloaded models |
| `lms ps` | List currently loaded (running) models |
| `lms load <model>` | Load a model into memory |
| `lms unload <model>` | Unload a model |
| `lms get <model>` | Download a model from Hub |
| `lms serve` | Start the LM Studio server (foreground) |
| `lms daemon start` | Start as background daemon |
| `lms daemon stop` | Stop daemon |
| `lms daemon status` | Check daemon status |
| `lms link` | Link CLI to a remote LM Studio instance (LM Link) |

## Quick Reference  <!-- all-tiers -->

```bash
# List available models (downloaded)
lms ls

# List loaded models
lms ps

# Load a model for inference
lms load qwen/qwen3-4b

# Download from Hub
lms get qwen/qwen3-4b --quantization Q4_K_M

# Start the API server (foreground)
lms serve --port 1234

# Background daemon
lms daemon start
lms daemon status
lms daemon stop

# Unload a model
lms unload qwen/qwen3-4b
```

## Load with Config  <!-- sonnet+ -->

```bash
lms load qwen/qwen3-4b \
  --context-length 8192 \
  --gpu-offload max
```

Options:
- `--context-length N` — override default context window
- `--gpu-offload max|auto|N` — GPU layers to offload
- `--port N` — server port (default 1234)

## Scripting Pattern  <!-- sonnet+ -->

```bash
#!/bin/bash
# CI / automation: ensure model is loaded before running tests

MODEL="qwen/qwen3-4b"

# Check if loaded
if ! lms ps | grep -q "$MODEL"; then
  echo "Loading $MODEL..."
  lms load "$MODEL"
fi

# Run your tests
python tests/test_inference.py
```

## Daemon Management  <!-- sonnet+ -->

```bash
# Start daemon (persists after shell exit)
lms daemon start --port 1234

# View logs
lms daemon logs

# Restart
lms daemon restart

# Auto-start with system (generates systemd unit)
lms daemon install-service   # Linux / llmster
```

## Cross-References  <!-- all-tiers -->

- [[lmstudio/overview.ctx|LM Studio Overview]] — headless deployment with `llmster`
- [[lmstudio/rest-api.ctx|REST API v1]] — API surface exposed by `lms serve`
- [[modules/lmstudio.ctx|openclaw lmstudio integration]] — openclaw checks model availability via REST, not CLI
