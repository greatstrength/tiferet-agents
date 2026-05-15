"""tiferet_agents Memory KB Adapter"""

# *** imports

# ** core
from typing import Dict, List, Optional

# ** app
from tiferet_kb.interfaces.document import DocumentService

from ..domain.memory import MemoryFact, MemoryNamespace
from ..interfaces.embedding import EmbeddingService
from ..interfaces.memory import MemoryService

# *** repos

# ** repo: memory_kb_adapter
class MemoryKBAdapter(MemoryService):
    '''
    MemoryService implementation backed by tiferet-kb's DocumentService.

    Maps MemoryNamespace → Document and MemoryFact → DocumentSection.
    Fact text is embedded via the EmbeddingService and stored in HDF5
    via DocumentService.embed_section.
    '''

    # * attribute: document_service
    document_service: DocumentService

    # * attribute: embedding_service
    embedding_service: EmbeddingService

    # * attribute: _namespace_cache
    _namespace_cache: Dict[str, MemoryNamespace]

    # * init
    def __init__(self, document_service: DocumentService, embedding_service: EmbeddingService):
        '''
        Initialize the memory KB adapter.

        :param document_service: The tiferet-kb document service.
        :type document_service: DocumentService
        :param embedding_service: The embedding service for vector generation.
        :type embedding_service: EmbeddingService
        '''

        # Set dependencies.
        self.document_service = document_service
        self.embedding_service = embedding_service
        self._namespace_cache = {}

    # * method: get_or_create_namespace
    def get_or_create_namespace(self, agent_id: str, name: str = 'default') -> MemoryNamespace:
        '''
        Get or create a memory namespace for an agent.

        Uses the document title convention "memory:{agent_id}:{name}" to
        find or create a corresponding tiferet-kb Document.

        :param agent_id: The agent identifier.
        :type agent_id: str
        :param name: The namespace name.
        :type name: str
        :return: The memory namespace.
        :rtype: MemoryNamespace
        '''

        # Check the cache first.
        cache_key = f'{agent_id}:{name}'
        if cache_key in self._namespace_cache:
            return self._namespace_cache[cache_key]

        # Search for an existing document with the memory namespace title.
        doc_title = f'memory:{agent_id}:{name}'
        docs = self.document_service.list()
        for doc in docs:
            title = getattr(doc, 'title', getattr(doc, 'name', ''))
            if title == doc_title:
                ns = MemoryNamespace(
                    id=doc.id,
                    agent_id=agent_id,
                    name=name,
                )
                self._namespace_cache[cache_key] = ns
                return ns

        # Create a new document for the namespace.
        from tiferet_kb.mappers import DocumentAggregate
        doc = DocumentAggregate(
            title=doc_title,
            description=f'Memory namespace for agent {agent_id}',
        )
        self.document_service.save(doc)

        # Build and cache the namespace.
        ns = MemoryNamespace(
            id=doc.id,
            agent_id=agent_id,
            name=name,
        )
        self._namespace_cache[cache_key] = ns
        return ns

    # * method: store_fact
    def store_fact(self, namespace_id: str, fact: MemoryFact) -> None:
        '''
        Persist a memory fact with its embedding.

        Performs deduplication by (subject, predicate): if a fact with
        the same subject and predicate exists and has lower or equal
        confidence, it is superseded. If it has higher confidence,
        the new fact is skipped.

        :param namespace_id: The namespace (document) identifier.
        :type namespace_id: str
        :param fact: The memory fact to store.
        :type fact: MemoryFact
        '''

        # Check for existing facts with the same (subject, predicate).
        existing_facts = self.list_facts(namespace_id)
        for existing in existing_facts:
            if existing.subject == fact.subject and existing.predicate == fact.predicate:
                # If existing has higher confidence, skip.
                if existing.confidence > fact.confidence:
                    return
                # Otherwise, supersede: remove the old fact.
                self.forget(namespace_id, existing.id)
                break

        # Create a document section for the fact.
        from tiferet_kb.mappers import DocumentSectionAggregate
        section = DocumentSectionAggregate(
            id=fact.id,
            document_id=namespace_id,
            title=f'{fact.subject} {fact.predicate}',
            content=fact.to_text(),
        )
        self.document_service.save_section(section)

        # Embed the fact text and store the embedding.
        embedding = self.embedding_service.embed_text(fact.to_text())
        self.document_service.embed_section(
            section_id=fact.id,
            embedding=embedding,
            model_name=self.embedding_service.get_model_name(),
        )

    # * method: recall
    def recall(self,
            namespace_id: str,
            query_embedding: List[float],
            limit: int = 5,
        ) -> List[MemoryFact]:
        '''
        Recall facts semantically similar to the query embedding.

        :param namespace_id: The namespace (document) identifier.
        :type namespace_id: str
        :param query_embedding: The query embedding vector.
        :type query_embedding: List[float]
        :param limit: Maximum results.
        :type limit: int
        :return: A list of memory facts ranked by similarity.
        :rtype: List[MemoryFact]
        '''

        # Search for similar sections in the namespace document.
        results = self.document_service.search_similar(
            query_embedding=query_embedding,
            limit=limit,
        )

        # Map results back to MemoryFact objects.
        all_facts = self.list_facts(namespace_id)
        facts_by_id = {f.id: f for f in all_facts}

        recalled = []
        for result in results:
            section_id = result.get('section_id', result.get('id', ''))
            if section_id in facts_by_id:
                recalled.append(facts_by_id[section_id])

        return recalled

    # * method: forget
    def forget(self, namespace_id: str, fact_id: str) -> None:
        '''
        Remove a fact from a namespace.

        :param namespace_id: The namespace (document) identifier.
        :type namespace_id: str
        :param fact_id: The fact (section) identifier.
        :type fact_id: str
        '''

        # Remove the embedding first (if it exists).
        try:
            self.document_service.remove_embedding(fact_id)
        except Exception:
            pass

        # Delete the section.
        self.document_service.delete_section(fact_id)

    # * method: list_facts
    def list_facts(self, namespace_id: str) -> List[MemoryFact]:
        '''
        List all facts in a namespace by reading sections from the document.

        :param namespace_id: The namespace (document) identifier.
        :type namespace_id: str
        :return: A list of memory facts.
        :rtype: List[MemoryFact]
        '''

        # Retrieve sections for the namespace document.
        sections = self.document_service.get_sections(namespace_id)

        # Map sections to MemoryFact objects.
        facts = []
        for section in sections:
            content = getattr(section, 'content', '')
            parts = content.split(' ', 2)
            if len(parts) >= 3:
                subject, predicate, obj = parts[0], parts[1], parts[2]
            elif len(parts) == 2:
                subject, predicate, obj = parts[0], parts[1], ''
            else:
                subject, predicate, obj = content, '', ''

            facts.append(MemoryFact(
                id=section.id,
                namespace_id=namespace_id,
                subject=subject,
                predicate=predicate,
                object=obj,
                created_at=getattr(section, 'created_at', None),
            ))

        return facts
