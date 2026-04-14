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



### Builtin (default)


SQLite-based. Works out of the box.

- **Keyword search** via FTS5 full-text indexing (BM25 scoring)
- **Vector search** via embeddings from any supported provider
- **Hybrid search** combining both retrieval approaches
- **CJK support** via trigram tokenization
- **sqlite-vec** for in-database vector queries (optional; graceful fallback)

**Index location:** `~/.openclaw/memory/<agentId>.sqlite`  
**File watching:** changes to `MEMORY.md` + `memory/*.md` trigger debounced reindex (1.5 s)  
**Auto-reindex:** when embedding provider, model, or chunking config changes

**Embedding providers (auto-detected in priority order):**

| Provider | ID | Auto-detected | Notes |
|----------|----|---------------|-------|
| OpenAI | `openai` | Yes | Default: `text-embedding-3-small` |
| Gemini | `gemini` | Yes | Supports multimodal (image + audio) |
| Voyage | `voyage` | Yes | |
| Mistral | `mistral` | Yes | |
| Ollama | `ollama` | No | Local; set explicitly |
| Local GGUF | `local` | Yes (first) | ~0.6 GB auto-download |

```json5
// Set provider explicitly
{
  agents: {
    defaults: {
      memorySearch: { provider: "openai" },
    },
  },
}
```


### QMD (local-first sidecar)


Adds reranking, query expansion, and extra-directory indexing over the builtin engine.

**Additional capabilities:**
- **Reranking + query expansion** for better recall
- **Index extra directories** — project docs, team notes, anything on disk
- **Index session transcripts** — recall earlier conversations
- **Fully local** — Bun + node-llama-cpp, auto-downloads GGUF models
- **Fallback** — if unavailable, OpenClaw falls back to builtin seamlessly

**Prerequisites:** `npm install -g @tobilu/qmd`, QMD on gateway `PATH`

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
      sessions: { enabled: true },  // index session transcripts
    },
  },
}
```

**Index location:** `~/.openclaw/agents/<agentId>/qmd/`  
**Model env vars (pass-through):** `QMD_EMBED_MODEL`, `QMD_RERANK_MODEL`, `QMD_GENERATE_MODEL`  
**First search slow:** QMD auto-downloads GGUF models (~2 GB) on first run

**Search modes:** `search` (default), `vsearch`, `query` (fallback retry on failure)


### Honcho (AI-native cross-session)


Plugin install required: `openclaw plugins install @honcho-ai/openclaw-honcho`

**Additional capabilities:**
- **Cross-session memory** — context carries across resets, compaction, and channel switches
- **User modeling** — profiles per user (preferences, facts, communication style)
- **Semantic search** over observations from past conversations
- **Multi-agent awareness** — parent agents track spawned sub-agents

**Honcho tools:**

| Tool | Type | What it does |
|------|------|-------------|
| `honcho_context` | data | Full user representation across sessions |
| `honcho_search_conclusions` | data | Semantic search over stored conclusions |
| `honcho_search_messages` | data | Find messages across sessions |
| `honcho_session` | data | Current session history and summary |
| `honcho_ask` | LLM | Ask about the user (`depth: 'quick'` or `'thorough'`) |

```json5
{
  plugins: {
    entries: {
      "openclaw-honcho": {
        config: {
          apiKey: "your-api-key",
          workspaceId: "openclaw",
          baseUrl: "https://api.honcho.dev",  // or localhost for self-hosted
        },
      },
    },
  },
}
```

**Honcho vs builtin:**
| | Builtin / QMD | Honcho |
|---|---|---|
| Storage | Workspace Markdown files | Dedicated service (local or hosted) |
| Cross-session | Via memory files | Automatic, built-in |
| User modeling | Manual (write to MEMORY.md) | Automatic profiles |
| Search | Vector + keyword (hybrid) | Semantic over observations |
| Multi-agent | Not tracked | Parent/child awareness |


## Dreaming (experimental)


Background memory consolidation system. Opt-in, disabled by default.

**Phase model:**

| Phase | Purpose | Durable write |
|-------|---------|---------------|
| Light | Sort and stage recent short-term material | No |
| Deep | Score and promote durable candidates | Yes (`MEMORY.md`) |
| REM | Reflect on themes and recurring ideas | No |

**Deep ranking signals:**

| Signal | Weight | Description |
|--------|--------|-------------|
| Relevance | 0.30 | Average retrieval quality |
| Frequency | 0.24 | Short-term signal accumulation |
| Query diversity | 0.15 | Distinct query/day contexts |
| Recency | 0.15 | Time-decayed freshness |
| Consolidation | 0.10 | Multi-day recurrence strength |
| Conceptual richness | 0.06 | Concept-tag density |

**Outputs:**
- `memory/.dreams/` — machine state (recall store, phase signals, locks)
- `DREAMS.md` — human-readable diary and sweep summaries
- `MEMORY.md` — written only by deep phase after passing all gate thresholds

**Auto-managed cron:** when enabled, `memory-core` creates one cron job for a full sweep (default: `0 3 * * *`)

```json5
{
  plugins: {
    entries: {
      "memory-core": {
        config: {
          dreaming: {
            enabled: true,
            frequency: "0 3 * * *",
            timezone: "America/Los_Angeles",
          },
        },
      },
    },
  },
}
```

**Slash command:** `/dreaming status | on | off | help`


## Memory Wiki Plugin


`memory-wiki` compiles durable memory into a provenance-rich knowledge vault.
It does **not** replace the active memory plugin — it sits beside it.

**Vault modes:**

| Mode | Description |
|------|-------------|
| `isolated` | Own vault, own sources, no dependency on memory-core |
| `bridge` | Reads public artifacts from active memory plugin via SDK seams |
| `unsafe-local` | Explicit same-machine escape hatch for local private paths |

**Wiki-native tools:** `wiki_status`, `wiki_search`, `wiki_get`, `wiki_apply`, `wiki_lint`

**Vault layout:**
```
<vault>/
  AGENTS.md       ← agent instructions for this vault
  WIKI.md         ← wiki overview
  entities/       ← things, people, systems, projects
  concepts/       ← ideas, abstractions, patterns
  syntheses/      ← compiled summaries and rollups
  sources/        ← imported raw material + bridge-backed pages
  reports/        ← generated dashboards
  .openclaw-wiki/ ← compiled artifacts (agent-digest.json, claims.jsonl)
```

**Structured claims frontmatter** — pages can carry `claims` with `id`, `text`,
`status`, `confidence`, `evidence[]` — this is what makes the wiki act like a
belief layer, not a passive note dump.

**Recommended hybrid pattern (local-first):**
- QMD as active memory backend (raw notes, session exports, extra collections)
- `memory-wiki` in `bridge` mode (stable entities, claims, dashboards)

```

# One broad recall pass

memory_search corpus=all


# Wiki-specific provenance-aware results

wiki_search + wiki_get
```


## CLI Patterns


```bash

# Memory

openclaw memory status                      # index status, provider, file count
openclaw memory search "query"              # test retrieval from command line
openclaw memory index --force               # rebuild index
openclaw memory promote [--apply] [--limit] # preview/apply dreaming promotions
openclaw memory promote-explain "topic"     # explain why entry would/would not promote
openclaw memory rem-harness [--json]        # preview REM reflections without writing
openclaw memory rem-backfill --path ./memory --stage-short-term
openclaw memory rem-backfill --rollback     # undo staged backfill artifacts


# Wiki

openclaw wiki ingest ./docs/
openclaw wiki lint
openclaw wiki compile
openclaw wiki search "query"
openclaw wiki doctor
openclaw wiki status


# Honcho

openclaw honcho setup
openclaw honcho status
openclaw honcho ask "<question>"
openclaw honcho search "<query>" [-k N] [-d D]
```


## Cross-References


- [[modules/agents.ctx|agents]] — consumes `memory_search` and `memory_get` as built-in tools; triggers pre-compaction flush
- [[modules/config.ctx|config]] — memory path, embedding provider config, `memorySearch.*`
- [[modules/infra.ctx|infra]] — file I/O, HTTP for embedding API calls
- [[modules/plugins.ctx|plugins]] — `memory-core`, `memory-wiki`, `openclaw-honcho` are plugin extensions
- [[modules/tasks.ctx|tasks]] — dreaming sweep cron job managed by `memory-core`
- [[architecture/AGENT_RUNTIME.ctx|AGENT_RUNTIME]] — workspace file layout, pre-compaction flush, daily notes lifecycle
