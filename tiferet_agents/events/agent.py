"""tiferet_agents Agent Events"""

# *** imports

# ** core
from typing import List

# ** app
from tiferet.events import DomainEvent

from ..assets import constants as const
from ..domain.agent import AgentConfiguration
from ..interfaces.agent import AgentService
from ..mappers.agent import AgentConfigurationAggregate

# *** events

# ** event: configure_agent
class ConfigureAgent(DomainEvent):
    '''
    Event to create or update an agent configuration.
    '''

    # * attribute: agent_service
    agent_service: AgentService

    # * init
    def __init__(self, agent_service: AgentService):
        '''
        Initialize the ConfigureAgent event.

        :param agent_service: The agent service for persistence.
        :type agent_service: AgentService
        '''

        # Set the agent service dependency.
        self.agent_service = agent_service

    # * method: execute
    @DomainEvent.parameters_required(['name'])
    def execute(self,
            name: str,
            id: str | None = None,
            description: str | None = None,
            provider: str | None = None,
            model: str | None = None,
            system_prompt: str | None = None,
            temperature: float | None = None,
            max_tokens: int | None = None,
            **kwargs,
        ) -> AgentConfiguration:
        '''
        Create or update an agent configuration.

        :param name: The agent name.
        :type name: str
        :param id: Optional explicit ID.
        :type id: str | None
        :param description: Optional description.
        :type description: str | None
        :param provider: Optional LLM provider.
        :type provider: str | None
        :param model: Optional model identifier.
        :type model: str | None
        :param system_prompt: Optional system prompt.
        :type system_prompt: str | None
        :param temperature: Optional temperature.
        :type temperature: float | None
        :param max_tokens: Optional max tokens.
        :type max_tokens: int | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created agent configuration.
        :rtype: AgentConfiguration
        '''

        # Build the aggregate construction kwargs.
        agent_kwargs = dict(name=name)
        if id:
            agent_kwargs['id'] = id
        if description:
            agent_kwargs['description'] = description
        if provider:
            agent_kwargs['provider'] = provider
        if model:
            agent_kwargs['model'] = model
        if system_prompt:
            agent_kwargs['system_prompt'] = system_prompt
        if temperature is not None:
            agent_kwargs['temperature'] = temperature
        if max_tokens is not None:
            agent_kwargs['max_tokens'] = max_tokens

        # Create the aggregate.
        agent = AgentConfigurationAggregate(**agent_kwargs)

        # Verify no duplicate exists.
        self.verify(
            expression=not self.agent_service.exists(agent.id),
            error_code=const.AGENT_ALREADY_EXISTS_ID,
            id=agent.id,
        )

        # Persist the agent.
        self.agent_service.save(agent)

        # Return the created agent.
        return agent


# ** event: get_agent
class GetAgent(DomainEvent):
    '''
    Event to retrieve an agent configuration by ID.
    '''

    # * attribute: agent_service
    agent_service: AgentService

    # * init
    def __init__(self, agent_service: AgentService):
        '''
        Initialize the GetAgent event.

        :param agent_service: The agent service for retrieval.
        :type agent_service: AgentService
        '''

        # Set the agent service dependency.
        self.agent_service = agent_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> AgentConfiguration:
        '''
        Retrieve an agent configuration by ID.

        :param id: The agent identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The agent configuration.
        :rtype: AgentConfiguration
        '''

        # Retrieve the agent.
        agent = self.agent_service.get(id)

        # Verify it exists.
        self.verify(
            expression=agent is not None,
            error_code=const.AGENT_NOT_FOUND_ID,
            agent_id=id,
        )

        # Return the agent.
        return agent


# ** event: list_agents
class ListAgents(DomainEvent):
    '''
    Event to list all agent configurations.
    '''

    # * attribute: agent_service
    agent_service: AgentService

    # * init
    def __init__(self, agent_service: AgentService):
        '''
        Initialize the ListAgents event.

        :param agent_service: The agent service for listing.
        :type agent_service: AgentService
        '''

        # Set the agent service dependency.
        self.agent_service = agent_service

    # * method: execute
    def execute(self, **kwargs) -> List[AgentConfiguration]:
        '''
        List all agent configurations.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A list of agent configurations.
        :rtype: List[AgentConfiguration]
        '''

        # Return all agents.
        return self.agent_service.list()


# ** event: remove_agent
class RemoveAgent(DomainEvent):
    '''
    Event to delete an agent configuration.
    '''

    # * attribute: agent_service
    agent_service: AgentService

    # * init
    def __init__(self, agent_service: AgentService):
        '''
        Initialize the RemoveAgent event.

        :param agent_service: The agent service for deletion.
        :type agent_service: AgentService
        '''

        # Set the agent service dependency.
        self.agent_service = agent_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> None:
        '''
        Delete an agent configuration by ID.

        :param id: The agent identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Verify the agent exists.
        self.verify(
            expression=self.agent_service.exists(id),
            error_code=const.AGENT_NOT_FOUND_ID,
            agent_id=id,
        )

        # Delete the agent.
        self.agent_service.delete(id)
