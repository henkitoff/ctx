---
module: modules/infra
type: codebase
depends_on: []
depended_by: [agents, gateway, config, secrets, plugins, channels, cli]
provides: [ensurePortAvailable, ensureBinary, installGaxiosFetchCompat, PortInUseError]
invariants:
  - "infra has no dependencies on other src/ modules — it is the dependency root"
  - "All outbound HTTP must use the configured fetch wrapper (no raw fetch)"
keywords: [infra, ports, tls, binaries, http, network, errors, diagnostics]
---

## Purpose


The `infra` module provides **infrastructure utilities**: port availability,
TLS setup, external binary provisioning (ffmpeg), HTTP client defaults, and
diagnostic event dispatch. It has **no dependencies** on other `src/` modules —
it is the dependency root that everything else builds on.

Key components:
- **`tls/`** — TLS certificate loading and server setup
- **`ports.ts`** — Port availability and process detection
- **`binaries.ts`** — External binary provisioning
- **`net/`** — Network utilities, outbound request defaults
- **`outbound/`** — HTTP client setup (gaxios, fetch compat)
- **`errors.ts`** — Graceful error formatting
- **`diagnostic-events.ts`** — Diagnostics event dispatch


## Public API


| Export | Type | Purpose |
|--------|------|---------|
| `ensurePortAvailable` | fn | Check port; throw `PortInUseError` if taken |
| `describePortOwner` | fn | Identify which process owns a port |
| `PortInUseError` | class | Structured error for port conflicts |
| `ensureBinary` | fn | Download/locate external binary (ffmpeg) |
| `installGaxiosFetchCompat` | fn | Install gaxios fetch compatibility shim |


## Invariants


1. `infra` has **zero dependencies** on other `src/` modules
2. All outbound HTTP uses the configured fetch wrapper — never raw `fetch` or `axios`
3. Port checks use `ensurePortAvailable()` — never catch raw `EADDRINUSE`


## Cross-References


- All `src/` modules depend on `infra/` — it is the foundation layer
- `gateway/` — TLS setup, port availability
- `agents/` — binary provisioning for media tools
