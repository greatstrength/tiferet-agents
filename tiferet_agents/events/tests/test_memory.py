"""tiferet_agents Memory Event Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events import DomainEvent

from ..memory import ExtractFacts, RecallMemory, ForgetFact
from ...domain.memory import MemoryFact
from ...interfaces.memory import MemoryService
from ...interfaces.embedding import EmbeddingService

# *** fixtures

# ** fixture: mock_memory_service
@pytest.fixture
def mock_memory_service():
    '''
    Mock MemoryService for testing.
    '''
    return mock.Mock(spec=MemoryService)

# ** fixture: mock_embedding_service
@pytest.fixture
def mock_embedding_service():
    '''
    Mock EmbeddingService for testing.
    '''
    svc = mock.Mock(spec=EmbeddingService)
    svc.embed_text.return_value = [0.1, 0.2, 0.3]
    svc.get_model_name.return_value = 'text-embedding-3-small'
    return svc

# ** fixture: sample_facts
@pytest.fixture
def sample_facts():
    '''
    Sample memory facts for testing.
    '''
    return [
        MemoryFact(
            id='fact-1',
            namespace_id='ns-1',
            subject='user',
            predicate='prefers',
            object='Python',
        ),
        MemoryFact(
            id='fact-2',
            namespace_id='ns-1',
            subject='user',
            predicate='works at',
            object='Acme Corp',
        ),
    ]

# *** tests

# ** test: extract_facts_success
def test_extract_facts_success(mock_memory_service, mock_embedding_service):
    '''
    Test successful fact extraction and storage.
    '''

    # Execute.
    result = DomainEvent.handle(
        ExtractFacts,
        dependencies={
            'memory_service': mock_memory_service,
            'embedding_service': mock_embedding_service,
        },
        namespace_id='ns-1',
        subject='user',
        predicate='prefers',
        object='dark mode',
        confidence=0.9,
        source='conv-123',
    )

    # Assert fact was created and stored.
    assert result.subject == 'user'
    assert result.predicate == 'prefers'
    assert result.object == 'dark mode'
    assert result.confidence == 0.9
    assert result.source == 'conv-123'
    mock_memory_service.store_fact.assert_called_once()


# ** test: recall_memory_success
def test_recall_memory_success(mock_memory_service, mock_embedding_service, sample_facts):
    '''
    Test successful memory recall.
    '''

    # Arrange: embedding service returns a vector, memory service returns facts.
    mock_memory_service.recall.return_value = sample_facts

    # Execute.
    result = DomainEvent.handle(
        RecallMemory,
        dependencies={
            'memory_service': mock_memory_service,
            'embedding_service': mock_embedding_service,
        },
        namespace_id='ns-1',
        query='What does the user prefer?',
        limit=5,
    )

    # Assert.
    assert len(result) == 2
    mock_embedding_service.embed_text.assert_called_once_with('What does the user prefer?')
    mock_memory_service.recall.assert_called_once_with(
        namespace_id='ns-1',
        query_embedding=[0.1, 0.2, 0.3],
        limit=5,
    )


# ** test: recall_memory_empty
def test_recall_memory_empty(mock_memory_service, mock_embedding_service):
    '''
    Test recall with no matching facts.
    '''

    # Arrange.
    mock_memory_service.recall.return_value = []

    # Execute.
    result = DomainEvent.handle(
        RecallMemory,
        dependencies={
            'memory_service': mock_memory_service,
            'embedding_service': mock_embedding_service,
        },
        namespace_id='ns-1',
        query='Something unrelated',
    )

    # Assert.
    assert result == []


# ** test: forget_fact_success
def test_forget_fact_success(mock_memory_service):
    '''
    Test successful fact removal.
    '''

    # Execute.
    DomainEvent.handle(
        ForgetFact,
        dependencies={'memory_service': mock_memory_service},
        namespace_id='ns-1',
        fact_id='fact-1',
    )

    # Assert.
    mock_memory_service.forget.assert_called_once_with('ns-1', 'fact-1')
