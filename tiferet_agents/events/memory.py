"""tiferet_agents Memory Events"""

# *** imports

# ** core
from typing import List

# ** app
from tiferet.events import DomainEvent

from ..domain.memory import MemoryFact
from ..interfaces.embedding import EmbeddingService
from ..interfaces.memory import MemoryService

# *** events

# ** event: extract_facts
class ExtractFacts(DomainEvent):
    '''
    Event to store an explicit fact triple in agent memory.

    Takes subject/predicate/object directly (LLM-based extraction
    is deferred to Phase 4). Stores the fact with its embedding
    via the memory service.
    '''

    # * attribute: memory_service
    memory_service: MemoryService

    # * attribute: embedding_service
    embedding_service: EmbeddingService

    # * init
    def __init__(self, memory_service: MemoryService, embedding_service: EmbeddingService):
        '''
        Initialize the ExtractFacts event.

        :param memory_service: The memory service for persistence.
        :type memory_service: MemoryService
        :param embedding_service: The embedding service for vector generation.
        :type embedding_service: EmbeddingService
        '''

        # Set dependencies.
        self.memory_service = memory_service
        self.embedding_service = embedding_service

    # * method: execute
    @DomainEvent.parameters_required(['namespace_id', 'subject', 'predicate', 'object'])
    def execute(self,
            namespace_id: str,
            subject: str,
            predicate: str,
            object: str,
            confidence: float = 1.0,
            source: str = 'system',
            **kwargs,
        ) -> MemoryFact:
        '''
        Store a fact triple in memory.

        :param namespace_id: The memory namespace identifier.
        :type namespace_id: str
        :param subject: The fact subject.
        :type subject: str
        :param predicate: The fact predicate.
        :type predicate: str
        :param object: The fact object.
        :type object: str
        :param confidence: Confidence score (0.0 to 1.0).
        :type confidence: float
        :param source: Fact provenance.
        :type source: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The stored memory fact.
        :rtype: MemoryFact
        '''

        # Create the fact.
        fact = MemoryFact(
            namespace_id=namespace_id,
            subject=subject,
            predicate=predicate,
            object=object,
            confidence=confidence,
            source=source,
        )

        # Store the fact via the memory service.
        self.memory_service.store_fact(namespace_id, fact)

        # Return the stored fact.
        return fact


# ** event: recall_memory
class RecallMemory(DomainEvent):
    '''
    Event to recall facts semantically similar to a query.

    Generates an embedding for the query text and retrieves
    matching facts from the memory service.
    '''

    # * attribute: memory_service
    memory_service: MemoryService

    # * attribute: embedding_service
    embedding_service: EmbeddingService

    # * init
    def __init__(self, memory_service: MemoryService, embedding_service: EmbeddingService):
        '''
        Initialize the RecallMemory event.

        :param memory_service: The memory service for retrieval.
        :type memory_service: MemoryService
        :param embedding_service: The embedding service for vector generation.
        :type embedding_service: EmbeddingService
        '''

        # Set dependencies.
        self.memory_service = memory_service
        self.embedding_service = embedding_service

    # * method: execute
    @DomainEvent.parameters_required(['namespace_id', 'query'])
    def execute(self,
            namespace_id: str,
            query: str,
            limit: int = 5,
            **kwargs,
        ) -> List[MemoryFact]:
        '''
        Recall facts similar to the query.

        :param namespace_id: The memory namespace identifier.
        :type namespace_id: str
        :param query: The query text for semantic search.
        :type query: str
        :param limit: Maximum number of facts to return.
        :type limit: int
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A list of memory facts ranked by similarity.
        :rtype: List[MemoryFact]
        '''

        # Generate the query embedding.
        query_embedding = self.embedding_service.embed_text(query)

        # Recall facts from the memory service.
        return self.memory_service.recall(
            namespace_id=namespace_id,
            query_embedding=query_embedding,
            limit=limit,
        )


# ** event: forget_fact
class ForgetFact(DomainEvent):
    '''
    Event to remove a fact from agent memory.
    '''

    # * attribute: memory_service
    memory_service: MemoryService

    # * init
    def __init__(self, memory_service: MemoryService):
        '''
        Initialize the ForgetFact event.

        :param memory_service: The memory service for removal.
        :type memory_service: MemoryService
        '''

        # Set the memory service dependency.
        self.memory_service = memory_service

    # * method: execute
    @DomainEvent.parameters_required(['namespace_id', 'fact_id'])
    def execute(self, namespace_id: str, fact_id: str, **kwargs) -> None:
        '''
        Remove a fact from memory.

        :param namespace_id: The namespace identifier.
        :type namespace_id: str
        :param fact_id: The fact identifier.
        :type fact_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Delegate to the memory service.
        self.memory_service.forget(namespace_id, fact_id)
