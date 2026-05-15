"""tiferet_agents Interfaces Tool"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** app
from tiferet.interfaces import Service

# *** interfaces

# ** interface: tool_service
class ToolService(Service):
    '''
    Service interface for managing agent tools.

    Provides registration, listing, and removal of tools
    on agent configurations via the underlying agent persistence.
    '''

    # * method: register
    @abstractmethod
    def register(self, agent_id: str, tool) -> None:
        '''
        Register a tool on an agent configuration.

        :param agent_id: The agent identifier.
        :type agent_id: str
        :param tool: The tool aggregate to register.
        :return: None
        :rtype: None
        '''
        raise NotImplementedError()

    # * method: list
    @abstractmethod
    def list(self, agent_id: str) -> List:
        '''
        List all tools for an agent.

        :param agent_id: The agent identifier.
        :type agent_id: str
        :return: A list of agent tools.
        :rtype: List
        '''
        raise NotImplementedError()

    # * method: remove
    @abstractmethod
    def remove(self, agent_id: str, tool_id: str) -> None:
        '''
        Remove a tool from an agent configuration.

        :param agent_id: The agent identifier.
        :type agent_id: str
        :param tool_id: The tool identifier.
        :type tool_id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError()
