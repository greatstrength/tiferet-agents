"""tiferet_agents — Agentic Extension for the Tiferet Framework"""

# *** exports

# ** app
# Wrap runtime imports in a try/except so that build tools can import
# __version__ without requiring the full dependency tree to be installed.
try:
    from .domain import (
        AgentConfiguration, AgentMemoryConfig, AgentTool,
        Conversation, Message,
        MemoryFact, MemoryNamespace,
    )
    from .interfaces import (
        AgentService, ConversationService, EmbeddingService,
        LLMProviderService, MemoryService, ToolService,
    )
    from .mappers import (
        AgentConfigurationAggregate,
        AgentConfigurationYamlObject,
        AgentToolAggregate,
        AgentToolYamlObject,
        ConversationAggregate,
        MessageAggregate,
    )
    from .events import (
        ApproveToolCall, DenyToolCall,
        SendMessage, SendMessageStream,
    )
    from .utils import (
        EmbeddingProviderFactory, GraphBuilder, LLMProviderFactory,
        PromptRenderer, RetryHandler, create_feature_tool,
    )
except Exception as e:
    import os, sys
    if not os.getenv('TIFERET_AGENTS_SILENT_IMPORTS'):
        print(f'Warning: Failed to import tiferet_agents modules: {e}', file=sys.stderr)

# *** version

__version__ = '0.1.0a4'
