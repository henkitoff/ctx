---
module: architecture/SANDBOX
type: architecture
purpose: Sandboxing — backends (Docker/SSH/OpenShell), modes, scope, tool policy, elevated mode
affects: [agents, plugins, nodes]

tags: [ctx/architecture]
---

## Overview  <!-- all-tiers -->

OpenClaw can run **tools inside sandbox backends** to reduce blast radius. The
Gateway stays on the host; tool execution runs in an isolated sandbox when enabled.

Three separate controls:

1. **Sandbox** (`agents.defaults.sandbox.*`) — decides **where tools run** (Docker vs host)
2. **Tool policy** (`tools.*`) — decides **which tools are available/allowed**
3. **Elevated** (`tools.elevated.*`) — exec-only escape hatch to run outside sandbox

These are independent. Sandbox restricts the execution environment; tool policy
controls which tools exist; elevated grants specific senders a host-exec bypass.

## Sandbox Modes and Scope  <!-- all-tiers -->

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

## Backends  <!-- all-tiers -->

| | Docker | SSH | OpenShell |
|---|---|---|---|
| Where it runs | Local container | Any SSH host | OpenShell managed sandbox |
| Setup | `scripts/sandbox-setup.sh` | SSH key + target host | OpenShell plugin enabled |
| Workspace model | Bind-mount or copy | Remote-canonical (seed once) | `mirror` or `remote` |
| Browser sandbox | Supported | Not supported | Not supported yet |
| Bind mounts | `docker.binds` | N/A | N/A |

### Docker Backend

Default. Executes via local Docker daemon socket (`/var/run/docker.sock`).

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        scope: "agent",
        backend: "docker",
        workspaceAccess: "rw",    // rw | ro | none
        docker: {
          setupCommand: "apt-get update && apt-get install -y git",
          binds: ["/host/path:/container/path:ro"],
          network: "none",        // "none" = no network access
        },
      },
    },
  },
}
```

**Docker-out-of-Docker (DooD) constraint:** if Gateway runs as a Docker container,
`workspace` config must use the **host's absolute path**, not the container's internal
path. Volume map must be identical on both sides (`-v /host/path:/host/path`).

**Bind mount security:**
- `docker.binds` pierces the sandbox filesystem — prefer `:ro` for sources/secrets
- `scope: "shared"` ignores per-agent binds (only global binds apply)
- Symlink-parent escapes are blocked: source paths validated before and after ancestor resolution
- Binding `/var/run/docker.sock` hands host control to the sandbox — only do this intentionally

### SSH Backend

Runs tools on any SSH-accessible machine.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "ssh",
        scope: "session",
        ssh: {
          target: "user@gateway-host:22",
          workspaceRoot: "/tmp/openclaw-sandboxes",
          strictHostKeyChecking: true,
          identityFile: "~/.ssh/id_ed25519",
          // Or via SecretRef:
          identityData: { source: "env", provider: "default", id: "SSH_IDENTITY" },
        },
      },
    },
  },
}
```

**Remote-canonical model:** seeds remote workspace from local once; after that file
tools run directly against remote. Changes are NOT synced back automatically.
`openclaw sandbox recreate` re-seeds from local.

### OpenShell Backend

Plugin-based managed remote sandbox. Two workspace modes:

- **`mirror`** — local workspace stays canonical; syncs local→remote before exec, remote→local after exec
- **`remote`** — remote workspace is canonical after initial seed; no sync back

```json5
{
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          mode: "remote",  // mirror | remote
          remoteWorkspaceDir: "/sandbox",
        },
      },
    },
  },
}
```

## Tool Policy  <!-- sonnet+ -->

Tool policy layers (applied independently of sandboxing):

1. **Tool profile** — `tools.profile` (base allowlist)
2. **Per-provider profile** — `tools.byProvider[provider].profile`
3. **Global allow/deny** — `tools.allow` / `tools.deny`
4. **Per-agent allow/deny** — `agents.list[].tools.allow` / `...deny`
5. **Sandbox-only allow/deny** — `tools.sandbox.tools.allow` / `...deny` (only active when sandboxed)

**Rules:**
- `deny` always wins
- If `allow` is non-empty, everything not listed is blocked
- Tool policy is the hard stop — `/exec` command cannot override a denied `exec` tool

**Tool groups (shorthands):**

| Group | Tools |
|-------|-------|
| `group:runtime` | `exec`, `process`, `code_execution` |
| `group:fs` | `read`, `write`, `edit`, `apply_patch` |
| `group:sessions` | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status` |
| `group:memory` | `memory_search`, `memory_get` |
| `group:web` | `web_search`, `x_search`, `web_fetch` |
| `group:ui` | `browser`, `canvas` |
| `group:automation` | `cron`, `gateway` |
| `group:media` | `image`, `image_generate`, `video_generate`, `tts` |
| `group:openclaw` | All built-in OpenClaw tools (excludes provider plugins) |

## Elevated Mode  <!-- sonnet+ -->

Exec-only escape hatch to run outside the sandbox for authorized senders.

- `/elevated on` — run exec outside sandbox for this session
- `/elevated full` — skip exec approvals for this session
- Does NOT grant extra tools (tool allow/deny still applies)
- Does NOT change anything when sandbox is off (already on host)

```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: {
        whatsapp: ["+15551234567"],
        discord: ["user-123456"],
      },
    },
  },
}
```

## Browser Sandbox  <!-- sonnet+ -->

Isolates browser tool on a dedicated Docker network:

```json5
{
  agents: {
    defaults: {
      sandbox: {
        browser: {
          autoStart: true,
          network: "openclaw-sandbox-browser",
          cdpSourceRange: "172.21.0.1/32",
          allowHostControl: false,
        },
      },
    },
  },
}
```

noVNC observer access is password-protected; OpenClaw emits a short-lived token URL.

## Debugging  <!-- sonnet+ -->

```bash
openclaw sandbox explain                        # effective settings for default agent
openclaw sandbox explain --session agent:main:main
openclaw sandbox explain --agent work
openclaw sandbox explain --json

# Sandbox lifecycle
openclaw sandbox list                           # list all sandbox runtimes
openclaw sandbox recreate [--agent <id>]        # re-seed workspace from local
openclaw sandbox status
```

**Common "sandbox jail" issues:**

- **"Tool X blocked by sandbox tool policy"** — add to `tools.sandbox.tools.allow` or remove from `tools.sandbox.tools.deny`
- **"I'm in non-main mode but my session is sandboxed"** — group/channel sessions are non-main; use `sandbox explain` to see the effective mode
- **DooD workspace errors** — ensure `workspace` config uses host path and volume map is identical

## Affected Modules  <!-- all-tiers -->

- [[modules/agents.ctx|agents]] — sandbox applies to all tool execution in agent loop
- [[modules/plugins.ctx|plugins]] — plugin hooks can observe sandboxed tool calls
- [[architecture/AGENT_RUNTIME.ctx|AGENT_RUNTIME]] — sandboxing section, workspace access modes
- [[architecture/MULTI_AGENT.ctx|MULTI_AGENT]] — per-agent sandbox config (`agents.list[].sandbox`)
