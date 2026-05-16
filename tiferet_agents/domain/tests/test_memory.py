"""tiferet_agents Memory Domain Tests"""

# *** imports

# ** infra

# ** app
from ..memory import MemoryFact, MemoryNamespace

# *** tests

# ** test: memory_fact_defaults
def test_memory_fact_defaults():
    '''
    Test that MemoryFact auto-derives id and created_at.
    '''

    # Create with required fields only.
    fact = MemoryFact(
        namespace_id='ns-1',
        subject='user',
        predicate='prefers',
        object='Python',
    )

    # Assert defaults are applied.
    assert fact.id
    assert fact.namespace_id == 'ns-1'
    assert fact.subject == 'user'
    assert fact.predicate == 'prefers'
    assert fact.object == 'Python'
    assert fact.confidence == 1.0
    assert fact.source == 'system'
    assert fact.created_at


# ** test: memory_fact_explicit_values
def test_memory_fact_explicit_values():
    '''
    Test creating a MemoryFact with explicit values.
    '''

    # Create with all fields.
    fact = MemoryFact(
        id='fact-1',
        namespace_id='ns-1',
        subject='Alice',
        predicate='works at',
        object='Acme Corp',
        confidence=0.8,
        source='conv-123',
    )

    # Assert explicit values.
    assert fact.id == 'fact-1'
    assert fact.confidence == 0.8
    assert fact.source == 'conv-123'


# ** test: memory_fact_to_text
def test_memory_fact_to_text():
    '''
    Test that to_text renders the triple as a readable string.
    '''

    # Create a fact.
    fact = MemoryFact(
        namespace_id='ns-1',
        subject='user',
        predicate='prefers',
        object='dark mode',
    )

    # Assert text rendering.
    assert fact.to_text() == 'user prefers dark mode'


# ** test: memory_namespace_defaults
def test_memory_namespace_defaults():
    '''
    Test that MemoryNamespace auto-derives id and created_at.
    '''

    # Create with required fields only.
    ns = MemoryNamespace(agent_id='agent-1')

    # Assert defaults.
    assert ns.id
    assert ns.agent_id == 'agent-1'
    assert ns.name == 'default'
    assert ns.description == ''
    assert ns.created_at


# ** test: memory_namespace_explicit
def test_memory_namespace_explicit():
    '''
    Test creating a MemoryNamespace with explicit values.
    '''

    # Create with all fields.
    ns = MemoryNamespace(
        id='ns-1',
        agent_id='agent-1',
        name='work',
        description='Work-related memories',
    )

    # Assert explicit values.
    assert ns.id == 'ns-1'
    assert ns.name == 'work'
    assert ns.description == 'Work-related memories'
