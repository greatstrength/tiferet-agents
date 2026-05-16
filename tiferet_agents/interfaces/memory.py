"""tiferet_agents Interfaces Memory"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** app
from tiferet.interfaces import Service

# *** interfaces

# ** interface: memory_service
class MemoryService(Service):
    '''
    Service interface for managing agent memory facts.

    Provides storage, semantic recall, and removal of triple-shaped
    facts within agent namespaces.
    '''

    # * method: get_or_create_namespace
    @abstractmethod
    def get_or_create_namespace(self, agent_id: str, name: str = 'default'):
        '''
        Get or create a memory namespace for an agent.

        :param agent_id: The agent identifier.
        :type agent_id: str
        :param name: The namespace name.
        :type name: str
        :return: The memory namespace.
        '''
        raise NotImplementedError()

    # * method: store_fact
    @abstractmethod
    def store_fact(self, namespace_id: str, fact) -> None:
        '''
        Persist a memory fact with its embedding.

        :param namespace_id: The namespace identifier.
        :type namespace_id: str
        :param fact: The memory fact to store.
        :return: None
        :rtype: None
        '''
        raise NotImplementedError()

    # * method: recall
    @abstractmethod
    def recall(self,
            namespace_id: str,
            query_embedding: List[float],
            limit: int = 5,
        ) -> List:
        '''
        Recall facts semantically similar to the query embedding.

        :param namespace_id: The namespace identifier.
        :type namespace_id: str
        :param query_embedding: The query embedding vector.
        :type query_embedding: List[float]
        :param limit: Maximum number of facts to return.
        :type limit: int
        :return: A list of memory facts ranked by similarity.
        :rtype: List
        '''
        raise NotImplementedError()

    # * method: forget
    @abstractmethod
    def forget(self, namespace_id: str, fact_id: str) -> None:
        '''
        Remove a fact from a namespace.

        :param namespace_id: The namespace identifier.
        :type namespace_id: str
        :param fact_id: The fact identifier.
        :type fact_id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError()

    # * method: list_facts
    @abstractmethod
    def list_facts(self, namespace_id: str) -> List:
        '''
        List all facts in a namespace.

        :param namespace_id: The namespace identifier.
        :type namespace_id: str
        :return: A list of memory facts.
        :rtype: List
        '''
        raise NotImplementedError()
