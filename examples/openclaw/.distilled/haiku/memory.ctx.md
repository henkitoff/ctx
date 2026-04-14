---
module: modules/memory
type: codebase
depends_on: [config, infra, plugins]
depended_by: [agents, gateway]
provides: [MemoryIndex, memorySearch, memoryGet, wikiSearch, ObsidianBridge]
invariants:
  - "Memory indexing is async — agents read from last completed index, not live files"
  - "memory_search and memory_get are agent tools — never called from gateway code directly"
  - "Pre-compaction memory flush runs as a silent NO_REPLY turn before summarization"
  - "Dreaming is opt-in and disabled by default — never auto-enabled"
  - "Long-term promotion writes ONLY to MEMORY.md — never to daily notes"
  - "QMD falls back to builtin SQLite automatically if the sidecar is unavailable"
keywords: [memory, wiki, vector, search, embeddings, dreaming, QMD, Honcho, SQLite, knowledge-base, obsidian, semantic, hybrid-search]

tags: [ctx/module]
---

## Purpose


The `memory` module provides three pluggable memory backends, a wiki knowledge
layer, and a background dreaming system for agents.

**Workspace files (loaded every session):**
| File | Role |
|------|------|
| `MEMORY.md` | Long-term durable memory — loaded every DM session |
| `memory/YYYY-MM-DD.md` | Daily notes — today and yesterday loaded automatically |
| `DREAMS.md` | Dream Diary + dreaming sweep summaries for human review |

**Agent tools (registered by active memory plugin):**
- `memory_search` — semantic/hybrid search over memory files
- `memory_get` — read a specific memory file or line range

**Memory backends (pluggable, mutually exclusive):**
- **Builtin** (default) — SQLite FTS5 + vector, no extra dependencies
- **QMD** — local-first sidecar with reranking and query expansion
- **Honcho** — AI-native cross-session memory with user modeling

**Companion layer:**
- **`memory-wiki` plugin** — compiled knowledge vault with provenance, claims, and dashboards


## Public API


| Export | Type | Purpose |
|--------|------|---------|
| `memorySearch` | fn | Semantic/hybrid search over indexed memory files |
| `memoryGet` | fn | Read a specific memory file or line range |
| `wikiSearch` | fn | Search compiled wiki pages (via memory-wiki plugin) |
| `wikiGet` | fn | Read a wiki page by id/path |
| `MemoryIndex` | class | Build, load, and query the embedding index |
| `ObsidianBridge` | class | Import and sync Obsidian vault notes |


## Invariants


1. **Async indexing** — index built in background; agents read last-completed snapshot
2. **Agent-only tools** — `memory_search` / `memory_get` are not called from gateway code
3. **Pre-compaction flush** — silent `NO_REPLY` turn writes facts to `memory/YYYY-MM-DD.md` before compaction
4. **Dreaming opt-in** — disabled by default; enable explicitly in plugin config
5. **Promotion gate** — `MEMORY.md` written only by deep phase after `minScore` + `minRecallCount` + `minUniqueQueries` all pass
6. **QMD fallback** — if QMD sidecar unavailable, falls back to builtin SQLite seamlessly
7. **Plugin boundary** — memory-wiki reads active memory plugin via public SDK seams only (`bridge` mode)


## Memory Backends



## Cross-References


- [[modules/agents.ctx|agents]] — consumes `memory_search` and `memory_get` as built-in tools; triggers pre-compaction flush
- [[modules/config.ctx|config]] — memory path, embedding provider config, `memorySearch.*`
- [[modules/infra.ctx|infra]] — file I/O, HTTP for embedding API calls
- [[modules/plugins.ctx|plugins]] — `memory-core`, `memory-wiki`, `openclaw-honcho` are plugin extensions
- [[modules/tasks.ctx|tasks]] — dreaming sweep cron job managed by `memory-core`
- [[architecture/AGENT_RUNTIME.ctx|AGENT_RUNTIME]] — workspace file layout, pre-compaction flush, daily notes lifecycle
