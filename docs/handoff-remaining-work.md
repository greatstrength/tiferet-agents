# Handoff: tiferet-agents — Remaining Work (v0.1.0a4 → v0.1.0b1)

**Project:** tiferet-agents  
**Repository:** https://github.com/greatstrength/tiferet-agents  
**Current Version:** 0.1.0a3 (tagged, on `v0.x-proto`)  
**Date:** May 15, 2026

## What Has Been Delivered

### v0.1.0a1 — Foundation Layer
The foundation layer. A developer can:
- Define agent configurations as `DomainObject` subclasses with auto-derived UUIDs/timestamps
- Persist agents to YAML via `AgentYamlRepository`
- Execute CRUD operations via `DomainEvent.handle` (ConfigureAgent, GetAgent, ListAgents, RemoveAgent)
- Send messages to agents via `SendMessage` (loads config → builds LLM → builds ReAct graph → invokes → persists conversation)
- Construct LLM models via `LLMProviderFactory` (OpenAI + optional Anthropic)
- Build LangGraph ReAct agents via `GraphBuilder` (wraps `create_react_agent`)

**Artifacts:** 31 files, ~2,300 lines, 16 tests. Tag: `v0.1.0a1`. PR: #1.

### v0.1.0a2 — Provider Abstraction & Graph Configuration
Agents are fully definable via YAML without code changes:
- **Multi-provider LLM support:** Google provider added to `LLMProviderFactory` with lazy `langchain-google-genai` import. `google` and `all` optional extras in `pyproject.toml`.
- **YAML-driven graph topology:** `graph_type` field on `AgentConfiguration` (default `react`). `GraphBuilder.build()` dispatches by type. `custom` reserved for future use.
- **Tool registration system:** `ToolService` interface. `RegisterTool`/`ListTools`/`RemoveTool` events. `GraphBuilder.load_tools()` dynamically imports tools from `module_path.class_name`. `SendMessage` wires loaded tools into the graph.
- **Configurable system prompts:** `PromptRenderer` utility with `SafeDict` for safe `str.format_map` interpolation. Built-in `{current_date}`, `{current_time}` variables. Rendered before graph building in `SendMessage`.

**Artifacts:** 17 files changed, ~900 lines added, 32 tests. Tag: `v0.1.0a2`. PR: #2.

### v0.1.0a3 — Memory & tiferet-kb Integration
Agents remember across conversations via triple-shaped facts:
- **Memory domain objects:** `MemoryFact` (subject/predicate/object triple with confidence + source provenance), `MemoryNamespace` (groups facts per agent).
- **Memory config:** `AgentMemoryConfig` on `AgentConfiguration` with `enabled`, `namespace`, `recall_limit`, `embedding_provider`, `embedding_model`.
- **Interfaces:** `MemoryService` (store_fact, recall, forget, list_facts, get_or_create_namespace). `EmbeddingService` (embed_text, embed_texts, get_model_name).
- **EmbeddingProviderFactory:** Wraps LangChain `OpenAIEmbeddings`/`GoogleGenerativeAIEmbeddings` with lazy imports.
- **Events:** `ExtractFacts` (explicit triple storage), `RecallMemory` (semantic search via embedding), `ForgetFact`.
- **tiferet-kb adapter:** `MemoryKBAdapter` maps MemoryNamespace→Document, MemoryFact→DocumentSection. Uses `embed_section()` for storage, `search_similar()` for recall.
- **Deduplication:** `store_fact()` checks existing facts by `(subject, predicate)` match. Higher confidence wins.
- **LangGraph memory tools:** `create_memory_tools()` produces `@tool`-decorated `recall_memory` and `store_memory` functions. `SendMessage` auto-wires them when `agent.memory.enabled`.
- **Dependency:** `tiferet-kb>=0.2.0a1` as `[memory]` optional extra.

**Artifacts:** 20 files changed, ~1,400 lines added, 41 tests. Tag: `v0.1.0a3`. PR: #3.

## Current Architecture Summary

```
tiferet_agents/
├── assets/               # Constants (error codes)
├── domain/               # AgentConfiguration, AgentTool, AgentMemoryConfig,
│                         #   Conversation, Message, MemoryFact, MemoryNamespace
├── events/               # Agent CRUD, SendMessage, Tool registration, Memory events
├── interfaces/           # AgentService, ConversationService, LLMProviderService,
│                         #   ToolService, EmbeddingService, MemoryService
├── mappers/              # Aggregate + YamlObject for agent, conversation
├── repos/                # AgentYamlRepository, MemoryKBAdapter
├── utils/                # GraphBuilder, LLMProviderFactory, PromptRenderer,
│                         #   EmbeddingProviderFactory, create_memory_tools
└── tests (co-located)    # 41 passing tests
```

**Key runtime flow (SendMessage):**
1. Load agent config → create LLM model
2. Render system prompt with `PromptRenderer`
3. Load tools from `module_path.class_name` via `GraphBuilder.load_tools()`
4. If `agent.memory.enabled`: create namespace, add `recall_memory`/`store_memory` tools
5. Build ReAct graph via `GraphBuilder.build()` (dispatched by `graph_type`)
6. Invoke graph → extract response → persist conversation

## What Remains

### Phase 4 — Human-in-the-Loop & Advanced Patterns (v0.1.0a4)

**Goal:** Production agent patterns.

| Issue | Description | Dependencies |
| --- | --- | --- |
| 4.1 Human-in-the-Loop | `interrupt()` integration. Per-tool `requires_approval` field on `AgentTool`. `ApproveToolCall`/`DenyToolCall` events. `GraphBuilder` wires interrupt nodes for flagged tools. | None (Phase 2 complete) |
| 4.2 Streaming Support | `SendMessageStream` event. Token-by-token streaming via `graph.stream()`. Event-based streaming for tool calls. Return type: generator or async iterator. | None |
| 4.3 Tiferet Feature Integration | Bidirectional bridge: (a) Tiferet features invoke agent graphs as steps in feature workflows. (b) Agents invoke Tiferet features as tools via `module_path: tiferet.contexts.feature`. | None (Phase 2 complete) |
| 4.4 Error Handling & Retry | LLM-specific error codes (rate limit, context length, auth). Exponential backoff with configurable max retries. Fallback prompts on context overflow. Token budget tracking in `AgentConfiguration`. | None |

**Implementation notes:**
- 4.1 requires adding `requires_approval: bool` to `AgentTool` domain, and a `HumanApprovalNode` wrapper in `GraphBuilder` that calls LangGraph's `interrupt()` before tool execution.
- 4.2 can use `graph.stream(inputs, config, stream_mode="messages")` for token streaming. Consider both sync generator and async iterator patterns.
- 4.3 is the key integration point with the parent `tiferet` framework. The agent-as-feature-step direction maps naturally to the existing `DomainEvent`/`DI` pattern. The feature-as-agent-tool direction wraps `App.run()` calls inside a `@tool` function.
- 4.4 should catch `openai.RateLimitError`, `anthropic.RateLimitError`, etc. and map to structured `TiferetError` codes.

### Phase 5 — Beta Release (v0.1.0b1)

**Goal:** Production-hardened, documented, published.

| Issue | Description | Dependencies |
| --- | --- | --- |
| 5.1 Production Checkpointers | SQLite/Postgres checkpointer selection via YAML `checkpointer` field on `AgentConfiguration`. LangGraph packages as optional extras (`pip install tiferet-agents[postgres]`). Wire into `GraphBuilder.build()`. | None |
| 5.2 Documentation | README rewrite, docs/core/ guides (architecture, events, memory, tools), YAML reference, API docs. AGENTS.md contributor orientation. | All phases |
| 5.3 CI/CD & Packaging | GitHub Actions (pytest matrix across Python 3.10-3.12, lint via ruff, optional-extras test matrix). PyPI publish workflow. Version bump automation. | All phases |
| 5.4 Example Applications | Chatbot example, KB-powered assistant (uses memory + tiferet-kb), CLI agent via `calc_cli.py` pattern, multi-tool agent. | Phases 2-3 |
| 5.5 Final Testing & Release | Integration test suite (`tests_int/`), regression tests for memory round-trips, benchmarks, release notes, PyPI publish of v0.1.0b1. | All phases |

## Architecture Decisions (Cumulative)

1. **No tiferet-postgres** — Postgres is scoped to LangGraph's own checkpointer packages as optional extras. A Tiferet-native Postgres layer is a separate future extension.
2. **HDF5-native embeddings** — tiferet-kb stores embedding vectors as contiguous numpy arrays. Brute-force cosine similarity for search. No external vector DB needed.
3. **Clean memory separation** — tiferet-agents generates embedding vectors (via `EmbeddingProviderFactory`); tiferet-kb owns storage and search (via `DocumentService`).
4. **Memory as tools, not graph nodes** — Memory exposed as `@tool`-decorated functions (`recall_memory`, `store_memory`) rather than custom LangGraph state/node patterns. Simpler, compatible with the standard ReAct topology.
5. **No Jinja2 for prompts** — `str.format_map` with `SafeDict` keeps prompts dependency-free. Sufficient for variable interpolation at current scale.
6. **Separate EmbeddingService** — Embedding models have a different API than chat models (`embed_query` vs `invoke`). `EmbeddingService` is a distinct interface from `LLMProviderService`.
7. **Proto-release workflow** — `v0.x-proto` → release branches → squash-merge → annotated tags.

## Suggested Next Steps

1. **Start Phase 4** from `v0.x-proto` — Human-in-the-loop (4.1) and streaming (4.2) are independent and can be parallelized.
2. **Add AGENTS.md** to tiferet-agents — contributor orientation document (deferred since a1).
3. **Integration tests** — The `tests_int/` directory is empty. Before beta, add end-to-end tests that exercise `SendMessage` with mocked LLM responses and real YAML configs.
