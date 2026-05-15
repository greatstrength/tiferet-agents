# Handoff: tiferet-agents — Remaining Work (v0.1.0a2 → v0.1.0b1)

**Project:** tiferet-agents  
**Repository:** https://github.com/greatstrength/tiferet-agents  
**Current Version:** 0.1.0a1 (tagged, on `v0.x-proto`)  
**Date:** May 15, 2026

## What Was Delivered (v0.1.0a1)

The foundation layer is complete and merged. A developer can:
- Define agent configurations as `DomainObject` subclasses with auto-derived UUIDs/timestamps
- Persist agents to YAML via `AgentYamlRepository`
- Execute CRUD operations via `DomainEvent.handle` (ConfigureAgent, GetAgent, ListAgents, RemoveAgent)
- Send messages to agents via `SendMessage` (loads config → builds LLM → builds ReAct graph → invokes → persists conversation)
- Construct LLM models via `LLMProviderFactory` (OpenAI + optional Anthropic)
- Build LangGraph ReAct agents via `GraphBuilder` (wraps `create_react_agent`)

**Artifacts:**
- 31 files, ~2,300 lines across domain/, interfaces/, mappers/, events/, utils/, repos/
- 16 passing tests (domain objects + domain events)
- YAML configs: `agent.yml`, `error.yml`
- Tag: `v0.1.0a1`
- PR: greatstrength/tiferet-agents#1 (squash-merged)

## What Remains

### Phase 2 — Provider Abstraction & Graph Configuration (v0.1.0a2)

**Goal:** Agents fully definable via YAML without code changes.

| Issue | Description | Dependencies |
| --- | --- | --- |
| 2.1 Multi-Provider LLM Support | Extend `LLMProviderFactory` for Anthropic, Google. Provider packages as optional extras in `pyproject.toml`. | None |
| 2.2 YAML-Driven Graph Topology | Add `graph` field to `AgentConfiguration` (react/plan-and-execute/custom). `GraphBuilder` reads topology from config. | 2.1 |
| 2.3 Tool Registration System | `RegisterTool`/`ListTools` events. Load tools from `module_path.class_name`. YAML-based tool config. Wire tools into `SendMessage` flow. | None |
| 2.4 Configurable System Prompts | Jinja2-style template variables in system prompts. Runtime injection of context. | None |

**Key gap from a1:** `SendMessage` currently builds graphs with no tools. 2.3 is the critical issue that makes agents actually useful.

### Phase 3 — Memory & tiferet-kb Integration (v0.1.0a3)

**Goal:** Agents remember across conversations.

**Prerequisite:** tiferet-kb v0.2.0a1 (embedding storage + semantic search). Handoff written to `tiferet-kb/docs/handoff-v0.2.0a1-embeddings.md`.

| Issue | Description | Dependencies |
| --- | --- | --- |
| 3.1 Memory Domain Objects | `MemoryFact` (triple-shaped: subject/predicate/object), `MemoryNamespace` | None |
| 3.2 Memory Service & Events | `MemoryService` interface. `ExtractFacts`, `RecallMemory`, `ForgetFact` events. | 3.1 |
| 3.3 LangGraph Memory Nodes | `persist` node (write facts), `recall` node (inject facts into prompt). Integrated into `GraphBuilder`. | 3.2 |
| 3.4 tiferet-kb Retrieval Adapter | `MemoryService` backed by `DocumentService.search_similar()`. HDF5-native embedding search. | 3.2, tiferet-kb v0.2.0a1 |
| 3.5 Deduplication & Contradiction | Fact dedup by `(subject, predicate)`. Confidence-based superseding. | 3.2 |
| 3.6 Memory YAML Configuration | Per-agent memory policies in `agent.yml`. | 3.3 |

**Design decision (from this session):** Embeddings stored as HDF5 arrays in tiferet-kb, not via Postgres/pgvector. Brute-force numpy cosine similarity is sufficient for expected scale (< 100K vectors). tiferet-agents generates embedding vectors via `LLMProviderService`; tiferet-kb owns storage and search.

### Phase 4 — Human-in-the-Loop & Advanced Patterns (v0.1.0a4)

**Goal:** Production agent patterns.

| Issue | Description | Dependencies |
| --- | --- | --- |
| 4.1 Human-in-the-Loop | `interrupt()` integration. Per-tool `requires_approval` in YAML. Resume/deny events. | Phase 2 |
| 4.2 Streaming Support | `SendMessageStream` event. Token-by-token and event-based streaming. | None |
| 4.3 Tiferet Feature Integration | Bidirectional bridge: Tiferet features invoke agent graphs; agents invoke features as tools. | Phase 2 |
| 4.4 Error Handling & Retry | LLM error codes, exponential backoff, fallback prompts, token budget management. | None |

### Phase 5 — Beta Release (v0.1.0b1)

**Goal:** Production-hardened, documented, published.

| Issue | Description | Dependencies |
| --- | --- | --- |
| 5.1 Production Checkpointers | SQLite/Postgres checkpointer selection via YAML. LangGraph packages as optional extras (`pip install tiferet-agents[postgres]`). | None |
| 5.2 Documentation | README, docs/core/ guides, YAML reference, API docs. | All phases |
| 5.3 CI/CD & Packaging | GitHub Actions (test matrix, lint), PyPI workflow, version bump. | All phases |
| 5.4 Example Applications | Chatbot, KB assistant, CLI agent examples. | Phases 2-3 |
| 5.5 Final Testing & Release | Regression suite, benchmarks, release notes, PyPI publish. | All phases |

## Parallel Workstream: tiferet-kb v0.2.0a1

Embedding storage and semantic search for tiferet-kb, required by Phase 3. Handoff document at:
`/Users/ashatz/Documents/GitHub/tiferet-kb/docs/handoff-v0.2.0a1-embeddings.md`

Estimated ~6 issues. Can proceed in parallel with tiferet-agents Phase 2.

## Architecture Decisions Made During This Session

1. **No tiferet-postgres** — Postgres is scoped to LangGraph's own checkpointer packages as optional extras. A Tiferet-native Postgres layer is a separate future extension.

2. **HDF5-native embeddings** — tiferet-kb stores embedding vectors as contiguous numpy arrays via `H5Service.create_array`. Brute-force cosine similarity for search. No external vector DB needed.

3. **Clean memory separation** — tiferet-agents generates embedding vectors (LLM call); tiferet-kb stores and searches them. Agents consume `DocumentService.search_similar()`.

4. **Proto-release workflow** — Documented in `greatstrength/tiferet` CONTRIBUTING.md. `v0.x-proto` → release branches → squash-merge → `proto-release` label.

## Suggested Next Steps

1. **Start Phase 2** from `v0.x-proto` — tool registration (2.3) is the highest-value issue since it makes agents actually do useful work.
2. **Start tiferet-kb v0.2.0a1** in parallel — the embedding extension is independent and derisks Phase 3.
3. **Add AGENTS.md** to tiferet-agents — contributor orientation document (deferred from a1 for brevity).
