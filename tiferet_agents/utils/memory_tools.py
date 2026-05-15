"""tiferet_agents Utils Memory Tools"""

# *** imports

# ** core
from typing import List

# ** infra
from langchain_core.tools import tool

# ** app
from ..domain.memory import MemoryFact
from ..interfaces.embedding import EmbeddingService
from ..interfaces.memory import MemoryService

# *** utils

# ** util: create_memory_tools
def create_memory_tools(
        memory_service: MemoryService,
        embedding_service: EmbeddingService,
        namespace_id: str,
        recall_limit: int = 5,
    ) -> List:
    '''
    Create LangChain tools for memory recall and storage.

    Returns a list of @tool-decorated functions that the agent can
    invoke during graph execution.

    :param memory_service: The memory service for persistence.
    :type memory_service: MemoryService
    :param embedding_service: The embedding service for vector generation.
    :type embedding_service: EmbeddingService
    :param namespace_id: The memory namespace identifier.
    :type namespace_id: str
    :param recall_limit: Default recall limit.
    :type recall_limit: int
    :return: A list of LangChain tools.
    :rtype: List
    '''

    @tool
    def recall_memory(query: str) -> str:
        """Search memory for facts relevant to the query. Returns matching facts as text."""

        # Generate query embedding.
        query_embedding = embedding_service.embed_text(query)

        # Recall facts.
        facts = memory_service.recall(
            namespace_id=namespace_id,
            query_embedding=query_embedding,
            limit=recall_limit,
        )

        # Format results.
        if not facts:
            return "No relevant memories found."

        lines = []
        for fact in facts:
            lines.append(f"- {fact.to_text()}")
        return "\n".join(lines)

    @tool
    def store_memory(subject: str, predicate: str, object: str) -> str:
        """Store a new fact in memory as a subject-predicate-object triple."""

        # Create and store the fact.
        fact = MemoryFact(
            namespace_id=namespace_id,
            subject=subject,
            predicate=predicate,
            object=object,
        )
        memory_service.store_fact(namespace_id, fact)

        return f"Stored: {fact.to_text()}"

    # Return both tools.
    return [recall_memory, store_memory]
