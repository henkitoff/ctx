---
module: architecture/SANDBOX
type: architecture
purpose: Sandboxing — backends (Docker/SSH/OpenShell), modes, scope, tool policy, elevated mode
affects: [agents, plugins, nodes]

tags: [ctx/architecture]
---

## Overview


OpenClaw can run **tools inside sandbox backends** to reduce blast radius. The
Gateway stays on the host; tool execution runs in an isolated sandbox when enabled.

Three separate controls:

1. **Sandbox** (`agents.defaults.sandbox.*`) — decides **where tools run** (Docker vs host)
2. **Tool policy** (`tools.*`) — decides **which tools are available/allowed**
3. **Elevated** (`tools.elevated.*`) — exec-only escape hatch to run outside sandbox

These are independent. Sandbox restricts the execution environment; tool policy
controls which tools exist; elevated grants specific senders a host-exec bypass.


## Sandbox Modes and Scope


**Mode** — controls when sandboxing is active:

| Mode | Behavior |
|------|---------|
| `"off"` | No sandboxing; tools run on host |
| `"non-main"` | Sandbox only non-main sessions (groups, channels, sub-agents) |
| `"all"` | Every session runs in a sandbox |

**Scope** — controls container reuse:

| Scope | Behavior |
|-------|---------|
| `"agent"` (default) | One container per agent |
| `"session"` | One container per session |
| `"shared"` | One container shared by all sandboxed sessions |

**What gets sandboxed:** tool execution (`exec`, `read`, `write`, `edit`, `apply_patch`, `process`), optionally browser.  
**Not sandboxed:** Gateway process itself, tools allowed via `tools.elevated`.


## Backends


| | Docker | SSH | OpenShell |
|---|---|---|---|
| Where it runs | Local container | Any SSH host | OpenShell managed sandbox |
| Setup | `scripts/sandbox-setup.sh` | SSH key + target host | OpenShell plugin enabled |
| Workspace model | Bind-mount or copy | Remote-canonical (seed once) | `mirror` or `remote` |
| Browser sandbox | Supported | Not supported | Not supported yet |
| Bind mounts | `docker.binds` | N/A | N/A |


## Affected Modules


- [[modules/agents.ctx|agents]] — sandbox applies to all tool execution in agent loop
- [[modules/plugins.ctx|plugins]] — plugin hooks can observe sandboxed tool calls
- [[architecture/AGENT_RUNTIME.ctx|AGENT_RUNTIME]] — sandboxing section, workspace access modes
- [[architecture/MULTI_AGENT.ctx|MULTI_AGENT]] — per-agent sandbox config (`agents.list[].sandbox`)
