"""tiferet_agents — Agentic Extension for the Tiferet Framework"""

# *** exports

# ** app
# Wrap runtime imports in a try/except so that build tools can import
# __version__ without requiring the full dependency tree to be installed.
try:
    from .domain import AgentConfiguration, AgentTool, Conversation, Message
    from .interfaces import AgentService, ConversationService, LLMProviderService
    from .mappers import (
        AgentConfigurationAggregate,
        AgentConfigurationYamlObject,
        AgentToolAggregate,
        AgentToolYamlObject,
        ConversationAggregate,
        MessageAggregate,
    )
except Exception as e:
    import os, sys
    if not os.getenv('TIFERET_AGENTS_SILENT_IMPORTS'):
        print(f'Warning: Failed to import tiferet_agents modules: {e}', file=sys.stderr)

# *** version

__version__ = '0.1.0a1'
