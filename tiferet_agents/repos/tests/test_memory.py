"""tiferet_agents MemoryKBAdapter Tests"""

# *** imports

# ** infra
from unittest import mock

import pytest

# ** app
from ...domain.memory import MemoryNamespace
from ...interfaces.embedding import EmbeddingService
from ...interfaces.memory import MemoryService
from ..memory import MemoryKBAdapter

# *** fixtures

# ** fixture: mock_document_service
@pytest.fixture
def mock_document_service():
    '''
    Mock DocumentService for testing.
    '''

    return mock.Mock()


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


# ** fixture: adapter
@pytest.fixture
def adapter(mock_document_service, mock_embedding_service) -> MemoryKBAdapter:
    '''
    Create a MemoryKBAdapter with mocked dependencies.
    '''

    return MemoryKBAdapter(
        document_service=mock_document_service,
        embedding_service=mock_embedding_service,
    )


# *** tests

# ** test: get_or_create_namespace_cache_hit
def test_get_or_create_namespace_cache_hit(adapter, mock_document_service):
    '''
    Test that a cached namespace is returned without calling the document service.
    '''

    # Pre-populate the cache.
    cached_ns = MemoryNamespace(
        id='cached-ns-id',
        agent_id='agent-1',
        name='default',
    )
    adapter._namespace_cache['agent-1:default'] = cached_ns

    # Execute.
    result = adapter.get_or_create_namespace('agent-1', 'default')

    # Assert cache hit returns the same object without listing docs.
    assert result is cached_ns
    mock_document_service.list.assert_not_called()


# ** test: get_or_create_namespace_existing_doc
def test_get_or_create_namespace_existing_doc(adapter, mock_document_service):
    '''
    Test that an existing document is found and mapped to a namespace.
    '''

    # Arrange: document service returns a doc matching the namespace title.
    existing_doc = mock.Mock()
    existing_doc.id = 'existing-doc-id'
    existing_doc.title = 'memory:agent-1:default'
    mock_document_service.list.return_value = [existing_doc]

    # Execute.
    result = adapter.get_or_create_namespace('agent-1', 'default')

    # Assert namespace was created from the existing doc.
    assert result.id == 'existing-doc-id'
    assert result.agent_id == 'agent-1'
    assert result.name == 'default'

    # Assert save was not called (doc already exists).
    mock_document_service.save.assert_not_called()

    # Assert the namespace was cached.
    assert 'agent-1:default' in adapter._namespace_cache


# ** test: get_or_create_namespace_new_doc_with_description
def test_get_or_create_namespace_new_doc_with_description(adapter, mock_document_service):
    '''
    Test that a new document is created with description when the
    backing DocumentAggregate model supports the field.
    '''

    # Arrange: no existing docs.
    mock_document_service.list.return_value = []

    # Patch DocumentAggregate to include 'description' in model_fields.
    mock_aggregate_cls = mock.Mock()
    mock_aggregate_cls.model_fields = {'title': mock.Mock(), 'description': mock.Mock()}

    # Capture the constructor call to return a mock doc with an id.
    mock_doc = mock.Mock()
    mock_doc.id = 'new-doc-id'
    mock_aggregate_cls.return_value = mock_doc

    with mock.patch('tiferet_kb.mappers.DocumentAggregate', mock_aggregate_cls):
        result = adapter.get_or_create_namespace('agent-1', 'default')

    # Assert the document was created with both title and description.
    mock_aggregate_cls.assert_called_once_with(
        title='memory:agent-1:default',
        description='Memory namespace for agent agent-1',
    )
    mock_document_service.save.assert_called_once_with(mock_doc)
    assert result.id == 'new-doc-id'
    assert result.agent_id == 'agent-1'


# ** test: get_or_create_namespace_new_doc_without_description
def test_get_or_create_namespace_new_doc_without_description(adapter, mock_document_service):
    '''
    Test that a new document is created with only title when the
    backing DocumentAggregate model does NOT have a description field.
    '''

    # Arrange: no existing docs.
    mock_document_service.list.return_value = []

    # Patch DocumentAggregate without 'description' in model_fields.
    mock_aggregate_cls = mock.Mock()
    mock_aggregate_cls.model_fields = {'title': mock.Mock()}

    mock_doc = mock.Mock()
    mock_doc.id = 'new-doc-id'
    mock_aggregate_cls.return_value = mock_doc

    with mock.patch('tiferet_kb.mappers.DocumentAggregate', mock_aggregate_cls):
        result = adapter.get_or_create_namespace('agent-1', 'default')

    # Assert the document was created with title only (no description).
    mock_aggregate_cls.assert_called_once_with(
        title='memory:agent-1:default',
    )
    mock_document_service.save.assert_called_once_with(mock_doc)
    assert result.id == 'new-doc-id'


# ** test: get_or_create_namespace_custom_name
def test_get_or_create_namespace_custom_name(adapter, mock_document_service):
    '''
    Test namespace creation with a custom (non-default) name.
    '''

    # Arrange: no matching docs.
    mock_document_service.list.return_value = []

    mock_aggregate_cls = mock.Mock()
    mock_aggregate_cls.model_fields = {'title': mock.Mock()}

    mock_doc = mock.Mock()
    mock_doc.id = 'custom-ns-id'
    mock_aggregate_cls.return_value = mock_doc

    with mock.patch('tiferet_kb.mappers.DocumentAggregate', mock_aggregate_cls):
        result = adapter.get_or_create_namespace('agent-1', 'work')

    # Assert the correct title convention.
    mock_aggregate_cls.assert_called_once_with(
        title='memory:agent-1:work',
    )
    assert result.name == 'work'
    assert 'agent-1:work' in adapter._namespace_cache
