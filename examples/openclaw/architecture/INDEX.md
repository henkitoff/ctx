# Architecture Index — OpenClaw

Cross-cutting patterns that span multiple modules.

| Document | What it covers |
|----------|---------------|
| [[AGENT_RUNTIME.ctx\|AGENT_RUNTIME]] | Workspace, bootstrap files, agent loop, skills, compaction, hooks, queue modes |
| [[AGENT_PIPELINE.ctx\|AGENT_PIPELINE]] | Model selection cascade, skill loading, ACP protocol, tool execution loop |
| [[MULTI_AGENT.ctx\|MULTI_AGENT]] | Multi-agent routing, bindings, sub-agents, per-agent sandbox and tool policy |
| [[MESSAGE_FLOW.ctx\|MESSAGE_FLOW]] | End-to-end: inbound message → agent → channel delivery |
| [[PLUGIN_SYSTEM.ctx\|PLUGIN_SYSTEM]] | Plugin boundary, manifest, adapter contracts, SDK |
| [[GATEWAY_PROTOCOL.ctx\|GATEWAY_PROTOCOL]] | Typed RPC, WebSocket lifecycle, versioning |
| [[LOCAL_INFERENCE.ctx\|LOCAL_INFERENCE]] | Local vs cloud routing, health checks, model ref schemes, graceful degradation |
| [[SANDBOX.ctx\|SANDBOX]] | Sandboxing backends (Docker/SSH/OpenShell), modes, scope, tool policy |
| [[DOCS_MAP.ctx\|DOCS_MAP]] | Complete documentation navigation map — all ~100 docs pages mapped |

## Navigation

[[INDEX\|OpenClaw INDEX]] · [[modules/agents.ctx\|agents]] · [[modules/plugins.ctx\|plugins]] · [[modules/gateway.ctx\|gateway]]
