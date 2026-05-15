"""tiferet_agents Agent Mappers"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List

# ** infra
from pydantic import AliasChoices, Field

# ** app
from tiferet.mappers import Aggregate, TransferObject

from ..domain.agent import AgentConfiguration, AgentTool

# *** mappers

# ** mapper: agent_tool_aggregate
class AgentToolAggregate(AgentTool, Aggregate):
    '''
    A mutable aggregate representation of an agent tool.
    '''

    # * method: rename
    def rename(self, name: str) -> None:
        '''
        Rename the tool.

        :param name: The new tool name.
        :type name: str
        '''

        # Update the name.
        self.name = name

    # * method: set_description
    def set_description(self, description: str) -> None:
        '''
        Set the tool description.

        :param description: The new description.
        :type description: str
        '''

        # Update the description.
        self.description = description


# ** mapper: agent_tool_yaml_object
class AgentToolYamlObject(AgentTool, TransferObject):
    '''
    A YAML transfer representation of an agent tool.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data.yaml': {
            'by_alias': True,
            'exclude': {'id'},
        },
    }

    # * attribute: parameters
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        serialization_alias='params',
        validation_alias=AliasChoices('params', 'parameters'),
        description='Static parameter overrides.',
    )

    # * method: map
    def map(self, **overrides) -> AgentToolAggregate:
        '''
        Map the YAML data to an agent tool aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new agent tool aggregate.
        :rtype: AgentToolAggregate
        '''

        # Serialize and construct the aggregate.
        return super().map(AgentToolAggregate, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, tool: AgentTool, **overrides) -> 'AgentToolYamlObject':
        '''
        Create an AgentToolYamlObject from an AgentTool model.

        :param tool: The agent tool to convert.
        :type tool: AgentTool
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new AgentToolYamlObject.
        :rtype: AgentToolYamlObject
        '''

        # Delegate to the base class.
        return super().from_model(tool, **overrides)


# ** mapper: agent_configuration_aggregate
class AgentConfigurationAggregate(AgentConfiguration, Aggregate):
    '''
    A mutable aggregate representation of an agent configuration.
    '''

    # * attribute: tools
    tools: List[AgentToolAggregate] = Field(
        default_factory=list,
        description='Mutable list of agent tool aggregates.',
    )

    # * method: rename
    def rename(self, name: str) -> None:
        '''
        Rename the agent.

        :param name: The new agent name.
        :type name: str
        '''

        # Update the name and timestamp.
        self.name = name
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: set_system_prompt
    def set_system_prompt(self, system_prompt: str) -> None:
        '''
        Set the agent system prompt.

        :param system_prompt: The new system prompt.
        :type system_prompt: str
        '''

        # Update the system prompt and timestamp.
        self.system_prompt = system_prompt
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: add_tool
    def add_tool(self, tool: AgentToolAggregate) -> None:
        '''
        Add a tool to the agent.

        :param tool: The tool aggregate to add.
        :type tool: AgentToolAggregate
        '''

        # Append the tool and update the timestamp.
        self.tools.append(tool)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: remove_tool
    def remove_tool(self, tool_id: str) -> None:
        '''
        Remove a tool from the agent by ID.

        :param tool_id: The tool identifier.
        :type tool_id: str
        '''

        # Filter out the tool and update the timestamp.
        self.tools = [t for t in self.tools if t.id != tool_id]
        self.updated_at = datetime.now(timezone.utc).isoformat()


# ** mapper: agent_configuration_yaml_object
class AgentConfigurationYamlObject(AgentConfiguration, TransferObject):
    '''
    A YAML transfer representation of an agent configuration.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'tools'}},
        'to_data.yaml': {
            'by_alias': True,
            'exclude': {'id', 'created_at', 'updated_at'},
        },
    }

    # * attribute: tools
    tools: List[AgentToolYamlObject] = Field(
        default_factory=list,
        description='YAML-serializable list of agent tools.',
    )

    # * method: map
    def map(self, **overrides) -> AgentConfigurationAggregate:
        '''
        Map the YAML data to an agent configuration aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new agent configuration aggregate.
        :rtype: AgentConfigurationAggregate
        '''

        # Map tools and delegate to base.
        return super().map(
            AgentConfigurationAggregate,
            tools=[tool.map() for tool in (self.tools or [])],
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, agent: AgentConfiguration, **overrides) -> 'AgentConfigurationYamlObject':
        '''
        Create an AgentConfigurationYamlObject from an AgentConfiguration model.

        :param agent: The agent configuration to convert.
        :type agent: AgentConfiguration
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new AgentConfigurationYamlObject.
        :rtype: AgentConfigurationYamlObject
        '''

        # Convert nested tools and delegate.
        return super().from_model(
            agent,
            tools=[
                AgentToolYamlObject.from_model(tool)
                for tool in agent.tools
            ],
            **overrides,
        )
