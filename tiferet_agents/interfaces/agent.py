"""tiferet_agents Interfaces Agent"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List, Optional

# ** app
from tiferet.interfaces import Service

# *** interfaces

# ** interface: agent_service
class AgentService(Service):
    '''
    Service interface for managing agent configurations.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if an agent configuration exists by ID.

        :param id: The agent configuration identifier.
        :type id: str
        :return: True if the agent exists, otherwise False.
        :rtype: bool
        '''
        raise NotImplementedError()

    # * method: get
    @abstractmethod
    def get(self, id: str):
        '''
        Retrieve an agent configuration by ID.

        :param id: The agent configuration identifier.
        :type id: str
        :return: The agent configuration aggregate, or None.
        '''
        raise NotImplementedError()

    # * method: list
    @abstractmethod
    def list(self) -> List:
        '''
        List all agent configurations.

        :return: A list of agent configuration aggregates.
        :rtype: List
        '''
        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, agent) -> None:
        '''
        Save or update an agent configuration.

        :param agent: The agent configuration aggregate to save.
        :return: None
        :rtype: None
        '''
        raise NotImplementedError()

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete an agent configuration by ID.

        :param id: The agent configuration identifier.
        :type id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError()
