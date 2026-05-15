"""tiferet_agents Tool Events"""

# *** imports

# ** core
from typing import List

# ** app
from tiferet.events import DomainEvent

from ..assets import constants as const
from ..domain.agent import AgentTool
from ..interfaces.agent import AgentService
from ..mappers.agent import AgentToolAggregate

# *** events

# ** event: register_tool
class RegisterTool(DomainEvent):
    '''
    Event to register a tool on an agent configuration.

    Creates an AgentToolAggregate from the provided parameters,
    verifies the agent exists and the tool is not a duplicate,
    then adds the tool to the agent and persists the change.
    '''

    # * attribute: agent_service
    agent_service: AgentService

    # * init
    def __init__(self, agent_service: AgentService):
        '''
        Initialize the RegisterTool event.

        :param agent_service: The agent service for persistence.
        :type agent_service: AgentService
        '''

        # Set the agent service dependency.
        self.agent_service = agent_service

    # * method: execute
    @DomainEvent.parameters_required(['agent_id', 'tool_id', 'name', 'module_path', 'class_name'])
    def execute(self,
            agent_id: str,
            tool_id: str,
            name: str,
            module_path: str,
            class_name: str,
            description: str | None = None,
            parameters: dict | None = None,
            **kwargs,
        ) -> AgentTool:
        '''
        Register a tool on an agent.

        :param agent_id: The agent configuration identifier.
        :type agent_id: str
        :param tool_id: The unique tool identifier.
        :type tool_id: str
        :param name: The human-readable tool name.
        :type name: str
        :param module_path: Python module path for the tool implementation.
        :type module_path: str
        :param class_name: Class or function name within the module.
        :type class_name: str
        :param description: Optional tool description.
        :type description: str | None
        :param parameters: Optional static parameter overrides.
        :type parameters: dict | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The registered tool.
        :rtype: AgentTool
        '''

        # Load the agent configuration.
        agent = self.agent_service.get(agent_id)
        self.verify(
            expression=agent is not None,
            error_code=const.AGENT_NOT_FOUND_ID,
            agent_id=agent_id,
        )

        # Verify the tool does not already exist on the agent.
        existing = agent.get_tool(tool_id)
        self.verify(
            expression=existing is None,
            error_code=const.AGENT_ALREADY_EXISTS_ID,
            id=f'{agent_id}.tools.{tool_id}',
        )

        # Build the tool aggregate.
        tool_kwargs = dict(
            id=tool_id,
            name=name,
            module_path=module_path,
            class_name=class_name,
        )
        if description:
            tool_kwargs['description'] = description
        if parameters:
            tool_kwargs['parameters'] = parameters

        tool = AgentToolAggregate(**tool_kwargs)

        # Add the tool to the agent and persist.
        agent.add_tool(tool)
        self.agent_service.save(agent)

        # Return the registered tool.
        return tool


# ** event: list_tools
class ListTools(DomainEvent):
    '''
    Event to list all tools for an agent configuration.
    '''

    # * attribute: agent_service
    agent_service: AgentService

    # * init
    def __init__(self, agent_service: AgentService):
        '''
        Initialize the ListTools event.

        :param agent_service: The agent service for retrieval.
        :type agent_service: AgentService
        '''

        # Set the agent service dependency.
        self.agent_service = agent_service

    # * method: execute
    @DomainEvent.parameters_required(['agent_id'])
    def execute(self, agent_id: str, **kwargs) -> List[AgentTool]:
        '''
        List all tools for an agent.

        :param agent_id: The agent identifier.
        :type agent_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A list of agent tools.
        :rtype: List[AgentTool]
        '''

        # Load the agent configuration.
        agent = self.agent_service.get(agent_id)
        self.verify(
            expression=agent is not None,
            error_code=const.AGENT_NOT_FOUND_ID,
            agent_id=agent_id,
        )

        # Return the agent's tools.
        return agent.tools


# ** event: remove_tool
class RemoveTool(DomainEvent):
    '''
    Event to remove a tool from an agent configuration.
    '''

    # * attribute: agent_service
    agent_service: AgentService

    # * init
    def __init__(self, agent_service: AgentService):
        '''
        Initialize the RemoveTool event.

        :param agent_service: The agent service for persistence.
        :type agent_service: AgentService
        '''

        # Set the agent service dependency.
        self.agent_service = agent_service

    # * method: execute
    @DomainEvent.parameters_required(['agent_id', 'tool_id'])
    def execute(self, agent_id: str, tool_id: str, **kwargs) -> None:
        '''
        Remove a tool from an agent.

        :param agent_id: The agent identifier.
        :type agent_id: str
        :param tool_id: The tool identifier.
        :type tool_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Load the agent configuration.
        agent = self.agent_service.get(agent_id)
        self.verify(
            expression=agent is not None,
            error_code=const.AGENT_NOT_FOUND_ID,
            agent_id=agent_id,
        )

        # Verify the tool exists.
        existing = agent.get_tool(tool_id)
        self.verify(
            expression=existing is not None,
            error_code=const.TOOL_NOT_FOUND_ID,
            tool_id=tool_id,
            agent_id=agent_id,
        )

        # Remove the tool and persist.
        agent.remove_tool(tool_id)
        self.agent_service.save(agent)
