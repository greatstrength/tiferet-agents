# tiferet-agents

Agentic extension for the [Tiferet](https://github.com/greatstrength/tiferet) framework — a lightweight, domain-driven wrapper around LangGraph that brings reliable, configurable agents into the Tiferet ecosystem.

## Features

- **YAML-driven agent configuration** — define agents, tools, memory, and prompts entirely in YAML
- **Multi-provider LLM support** — OpenAI (default), Anthropic, and Google Generative AI via optional extras
- **Tool registration** — dynamically load and wire tools from `module_path.class_name` definitions
- **Memory** — triple-shaped fact storage with semantic recall via tiferet-kb integration
- **Human-in-the-loop** — per-tool `requires_approval` with LangGraph interrupt/resume
- **Streaming** — token-by-token streaming via `SendMessageStream` event
- **Tiferet feature bridge** — invoke Tiferet features as agent tools with `create_feature_tool()`
- **Error handling & retry** — exponential backoff with LLM-specific error classification
- **Production checkpointers** — memory, SQLite, or Postgres state persistence

## Installation

```bash
pip install tiferet-agents
```

### Optional extras

```bash
pip install tiferet-agents[anthropic]    # Anthropic provider
pip install tiferet-agents[google]       # Google Generative AI provider
pip install tiferet-agents[memory]       # tiferet-kb memory integration
pip install tiferet-agents[sqlite]       # SQLite checkpointer
pip install tiferet-agents[postgres]     # Postgres checkpointer
pip install tiferet-agents[all]          # All optional dependencies
```

## Quick Start

### 1. Define an agent in YAML

```yaml
# app/configs/agent.yml
agents:
  my_assistant:
    name: My Assistant
    description: A helpful conversational assistant
    provider: openai
    model: gpt-4o-mini
    system_prompt: You are a helpful assistant. Today is {current_date}.
    temperature: 0.7
```

### 2. Send a message

```python
from tiferet_agents import SendMessage
from tiferet.events import DomainEvent

result = DomainEvent.handle(
    SendMessage,
    dependencies={
        'agent_service': agent_service,
        'conversation_service': conversation_service,
        'llm_provider_service': llm_provider_service,
    },
    agent_id='my_assistant',
    message='Hello, how are you?',
)
print(result.content)
```

## YAML Configuration Reference

```yaml
agents:
  <agent_id>:
    name: string              # Required
    description: string       # Optional
    provider: string          # Default: openai (openai|anthropic|google)
    model: string             # Default: gpt-4o-mini
    system_prompt: string     # Supports {current_date}, {current_time} variables
    temperature: float        # Default: 0.7
    max_tokens: int           # Optional
    graph_type: string        # Default: react
    checkpointer: string      # Default: memory (memory|sqlite|postgres)
    checkpointer_config:      # Optional checkpointer settings
      db_path: string         # For sqlite
    max_retries: int          # Default: 3
    memory:
      enabled: bool
      namespace: string
      recall_limit: int
      embedding_provider: str
      embedding_model: str
    tools:
      - id: string
        name: string
        module_path: string
        class_name: string
        requires_approval: bool
        params: {}
```

## Architecture

```
tiferet_agents/
├── assets/       # Error codes and constants
├── domain/       # Domain objects (AgentConfiguration, Conversation, Memory)
├── events/       # Domain events (SendMessage, CRUD, approval, tools, memory)
├── interfaces/   # Service contracts (AgentService, LLMProviderService, etc.)
├── mappers/      # Aggregates and YAML transfer objects
├── repos/        # YAML-backed service implementations
└── utils/        # GraphBuilder, LLMProviderFactory, CheckpointerFactory, etc.
```

See [AGENTS.md](AGENTS.md) for contributor orientation.

## License

BSD-3-Clause
