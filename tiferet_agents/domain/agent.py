"""tiferet_agents Agent Domain"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

# ** infra
from pydantic import Field, model_validator

# ** app
from tiferet.domain import DomainObject

# *** models

# ** model: agent_tool
class AgentTool(DomainObject):
    '''
    A tool available to an agent for execution during graph processing.

    Each tool maps to a callable (identified by module_path + class_name)
    that the LangGraph runtime can invoke when the LLM requests a tool call.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='Unique identifier for this tool.',
    )

    # * attribute: name
    name: str = Field(
        ...,
        description='Human-readable tool name.',
    )

    # * attribute: description
    description: str = Field(
        default='',
        description='Description of what the tool does, shown to the LLM.',
    )

    # * attribute: module_path
    module_path: str = Field(
        ...,
        description='Python module path containing the tool implementation.',
    )

    # * attribute: class_name
    class_name: str = Field(
        ...,
        description='Class or function name within the module.',
    )

    # * attribute: parameters
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        description='Static parameter overrides passed to the tool at init.',
    )


# ** model: agent_configuration
class AgentConfiguration(DomainObject):
    '''
    Configuration for an LLM-powered agent.

    Defines the LLM provider, model, system prompt, tools, and tuning
    parameters needed to build and execute a LangGraph agent graph.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='Unique identifier for this agent configuration.',
    )

    # * attribute: name
    name: str = Field(
        ...,
        description='Human-readable agent name.',
    )

    # * attribute: description
    description: str = Field(
        default='',
        description='Description of the agent purpose.',
    )

    # * attribute: provider
    provider: str = Field(
        default='openai',
        description='LLM provider name (e.g., openai, anthropic).',
    )

    # * attribute: model
    model: str = Field(
        default='gpt-4o-mini',
        description='Model identifier within the provider.',
    )

    # * attribute: system_prompt
    system_prompt: str = Field(
        default='You are a helpful assistant.',
        description='System prompt injected at the start of every conversation.',
    )

    # * attribute: temperature
    temperature: float = Field(
        default=0.7,
        description='Sampling temperature for the LLM.',
    )

    # * attribute: max_tokens
    max_tokens: Optional[int] = Field(
        default=None,
        description='Maximum tokens in the LLM response.',
    )

    # * attribute: graph_type
    graph_type: str = Field(
        default='react',
        description='Graph topology type (react, custom).',
    )

    # * attribute: tools
    tools: List[AgentTool] = Field(
        default_factory=list,
        description='List of tools available to this agent.',
    )

    # * attribute: created_at
    created_at: str = Field(
        ...,
        description='ISO 8601 creation timestamp.',
    )

    # * attribute: updated_at
    updated_at: str = Field(
        ...,
        description='ISO 8601 last-updated timestamp.',
    )

    # * method: _derive_defaults (validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_defaults(cls, data: Any) -> Any:
        '''
        Derive default values for id, created_at, and updated_at when absent.

        :param data: The raw input data.
        :type data: Any
        :return: The augmented input data.
        :rtype: Any
        '''

        # Only mutate dict-shaped inputs.
        if not isinstance(data, dict):
            return data
        data = dict(data)

        # Generate a UUID if id is not provided.
        if not data.get('id'):
            data['id'] = str(uuid4())

        # Set timestamps if not provided.
        now = datetime.now(timezone.utc).isoformat()
        if not data.get('created_at'):
            data['created_at'] = now
        if not data.get('updated_at'):
            data['updated_at'] = now

        # Return the augmented data.
        return data

    # * method: get_tool
    def get_tool(self, tool_id: str) -> Optional[AgentTool]:
        '''
        Get a tool by its identifier.

        :param tool_id: The tool identifier.
        :type tool_id: str
        :return: The AgentTool, or None if not found.
        :rtype: AgentTool | None
        '''

        # Search tools by id.
        for tool in self.tools:
            if tool.id == tool_id:
                return tool
        return None
