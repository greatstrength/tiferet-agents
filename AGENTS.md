# AGENTS.md — tiferet-agents (v0.1.0b1)

## Project Overview

**tiferet-agents** is the official agentic extension for the Tiferet framework. It provides a domain-driven wrapper around LangGraph for building configurable, tool-equipped, memory-enabled LLM agents.

- **Repository:** https://github.com/greatstrength/tiferet-agents
- **Python:** ≥ 3.10
- **Core dependencies:** tiferet, langgraph, langchain-openai, langchain-core

## Architecture

### Layer Overview

```
tiferet_agents/
├── assets/         Constants (error codes)
├── domain/         DomainObject subclasses: AgentConfiguration, AgentTool,
│                     Conversation, Message, MemoryFact, MemoryNamespace
├── events/         DomainEvent subclasses: agent CRUD, SendMessage,
│                     SendMessageStream, approval, tool registration, memory
├── interfaces/     Service ABCs: AgentService, ConversationService,
│                     LLMProviderService, ToolService, EmbeddingService, MemoryService
├── mappers/        Aggregate + YamlObject for agent, conversation
├── repos/          YAML-backed Service implementations
├── utils/          GraphBuilder, LLMProviderFactory, CheckpointerFactory,
│                     EmbeddingProviderFactory, PromptRenderer, RetryHandler,
│                     create_memory_tools, create_feature_tool
└── tests_int/      Integration tests
```

### Runtime Flow (SendMessage)

1. Load agent config via `AgentService`
2. Create LLM model via `LLMProviderFactory`
3. Render system prompt with `PromptRenderer`
4. Load tools via `GraphBuilder.load_tools()`
5. If memory enabled: create namespace, add memory tools
6. Create checkpointer via `CheckpointerFactory`
7. Build ReAct graph via `GraphBuilder.build()`
8. Invoke graph → extract response → persist conversation

## Structured Code Style

All code follows Tiferet's artifact comment hierarchy:

- `# *** <section>` — Top-level: imports, exports, models, events, etc.
- `# ** <category>: <name>` — Mid-level: individual components
- `# * <component>` — Low-level: attribute, init, method

Use RST docstrings with `:param`, `:type`, `:return`, `:rtype`.

## Testing

- **Framework:** pytest
- **Co-located tests:** `<package>/tests/` directories
- **Integration tests:** `tiferet_agents/tests_int/`
- **Run:** `pytest tiferet_agents/`
- **Event testing:** Always use `DomainEvent.handle(EventClass, dependencies={...}, **kwargs)`

## Branching

- Feature branches from `v0.x-proto` (or release branch)
- PRs target the release branch
- Release branches merge into `v0.x-proto`
- Annotated tags for each release

## Contributing

1. Tie work to a GitHub issue
2. Follow structured code style
3. Include `Co-Authored-By: Oz <oz-agent@warp.dev>` when collaborating with AI
4. Tests required for all new events and utilities
