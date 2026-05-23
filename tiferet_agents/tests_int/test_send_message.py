"""tiferet_agents Integration Tests — SendMessage"""

# *** imports

# ** infra
from unittest import mock

import pytest
from tiferet.assets.exceptions import TiferetError

# ** app
from tiferet.events import DomainEvent

from ..events.conversation import SendMessage
from ..interfaces.agent import AgentService
from ..interfaces.conversation import ConversationService
from ..interfaces.llm import LLMProviderService
from ..mappers.agent import AgentConfigurationAggregate
from ..domain.agent import AgentMemoryConfig
from ..domain.memory import MemoryNamespace
from ..interfaces.embedding import EmbeddingService
from ..interfaces.memory import MemoryService
from ..utils.graph import GraphBuilder
from ..utils.memory_tools import create_memory_tools

# *** fixtures

# ** fixture: sample_agent
@pytest.fixture
def sample_agent():
    '''
    A fully configured agent aggregate for integration testing.
    '''
    return AgentConfigurationAggregate(
        id='int-test-agent',
        name='Integration Test Agent',
        provider='openai',
        model='gpt-4o-mini',
        system_prompt='You are a test assistant.',
        temperature=0.0,
    )

# ** fixture: mock_services
@pytest.fixture
def mock_services(sample_agent):
    '''
    Mock services wired for SendMessage integration testing.
    '''

    agent_service = mock.Mock(spec=AgentService)
    agent_service.get.return_value = sample_agent

    conversation_service = mock.Mock(spec=ConversationService)
    conversation_service.get.return_value = None

    llm_service = mock.Mock(spec=LLMProviderService)
    mock_model = mock.Mock()
    llm_service.create_model.return_value = mock_model

    return {
        'agent_service': agent_service,
        'conversation_service': conversation_service,
        'llm_provider_service': llm_service,
        'mock_model': mock_model,
    }

# *** tests

# ** test: send_message_full_flow
def test_send_message_full_flow(mock_services, sample_agent):
    '''
    Integration test: full SendMessage flow with mocked LLM.
    Verifies the end-to-end orchestration from agent load to conversation persistence.
    '''

    # Patch GraphBuilder to avoid real LangGraph graph construction.
    mock_graph = mock.Mock()
    mock_graph.invoke.return_value = {
        'messages': [mock.Mock(content='Hello! I am your test assistant.')]
    }

    with mock.patch.object(GraphBuilder, 'build', return_value=mock_graph):
        with mock.patch.object(GraphBuilder, 'load_tools', return_value=[]):

            # Execute SendMessage.
            result = DomainEvent.handle(
                SendMessage,
                dependencies={
                    'agent_service': mock_services['agent_service'],
                    'conversation_service': mock_services['conversation_service'],
                    'llm_provider_service': mock_services['llm_provider_service'],
                },
                agent_id='int-test-agent',
                message='Hello, are you there?',
            )

    # Assert the response message was created.
    assert result is not None
    assert result.content == 'Hello! I am your test assistant.'
    assert result.role == 'ai'

    # Assert the agent was loaded.
    mock_services['agent_service'].get.assert_called_once_with('int-test-agent')

    # Assert the LLM model was created with agent config.
    mock_services['llm_provider_service'].create_model.assert_called_once_with(
        provider='openai',
        model='gpt-4o-mini',
        temperature=0.0,
        max_tokens=None,
    )

    # Assert the conversation was persisted.
    mock_services['conversation_service'].save.assert_called_once()

    # Verify the saved conversation has both user and AI messages.
    saved_conversation = mock_services['conversation_service'].save.call_args[0][0]
    assert len(saved_conversation.messages) == 2
    assert saved_conversation.messages[0].role == 'human'
    assert saved_conversation.messages[1].role == 'ai'


# ** test: send_message_agent_not_found
def test_send_message_agent_not_found():
    '''
    Integration test: SendMessage raises error when agent is not found.
    '''

    agent_service = mock.Mock(spec=AgentService)
    agent_service.get.return_value = None

    conversation_service = mock.Mock(spec=ConversationService)
    llm_service = mock.Mock(spec=LLMProviderService)

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            SendMessage,
            dependencies={
                'agent_service': agent_service,
                'conversation_service': conversation_service,
                'llm_provider_service': llm_service,
            },
            agent_id='nonexistent-agent',
            message='Hello?',
        )


# ** test: send_message_with_prompt_context
def test_send_message_with_prompt_context(mock_services, sample_agent):
    '''
    Integration test: verify prompt rendering with context variables.
    '''

    # Update agent to use prompt variables.
    sample_agent.system_prompt = 'You are {agent_name}. Today is {current_date}.'

    mock_graph = mock.Mock()
    mock_graph.invoke.return_value = {
        'messages': [mock.Mock(content='I am Integration Test Agent.')]
    }

    with mock.patch.object(GraphBuilder, 'build', return_value=mock_graph) as mock_build:
        with mock.patch.object(GraphBuilder, 'load_tools', return_value=[]):

            DomainEvent.handle(
                SendMessage,
                dependencies={
                    'agent_service': mock_services['agent_service'],
                    'conversation_service': mock_services['conversation_service'],
                    'llm_provider_service': mock_services['llm_provider_service'],
                },
                agent_id='int-test-agent',
                message='Who are you?',
            )

    # Verify the graph was built with a rendered prompt (not raw template).
    build_call = mock_build.call_args
    agent_for_graph = build_call.kwargs.get('agent_config') or build_call[1].get('agent_config')
    assert '{agent_name}' not in agent_for_graph.system_prompt
    assert 'Integration Test Agent' in agent_for_graph.system_prompt


# ** test: send_message_missing_required_params
def test_send_message_missing_required_params(mock_services):
    '''
    Integration test: SendMessage requires agent_id and message.
    '''

    with pytest.raises(TiferetError):
        DomainEvent.handle(
            SendMessage,
            dependencies={
                'agent_service': mock_services['agent_service'],
                'conversation_service': mock_services['conversation_service'],
                'llm_provider_service': mock_services['llm_provider_service'],
            },
            # Missing both agent_id and message.
        )


# ** test: send_message_memory_enabled_first_message
def test_send_message_memory_enabled_first_message():
    '''
    Integration test: a memory-enabled agent can initialize, create its
    namespace, load memory tools, and reach the LLM call boundary on
    the first message without compatibility failures.
    '''

    # Build a memory-enabled agent configuration.
    memory_agent = AgentConfigurationAggregate(
        id='memory-test-agent',
        name='Memory Test Agent',
        provider='openai',
        model='gpt-4o-mini',
        system_prompt='You are a test assistant with memory.',
        temperature=0.0,
        memory=AgentMemoryConfig(
            enabled=True,
            namespace='default',
            recall_limit=5,
        ),
    )

    # Wire mock services.
    agent_service = mock.Mock(spec=AgentService)
    agent_service.get.return_value = memory_agent

    conversation_service = mock.Mock(spec=ConversationService)
    conversation_service.get.return_value = None

    llm_service = mock.Mock(spec=LLMProviderService)
    llm_service.create_model.return_value = mock.Mock()

    # Mock memory service: get_or_create_namespace returns a namespace.
    memory_service = mock.Mock(spec=MemoryService)
    memory_service.get_or_create_namespace.return_value = MemoryNamespace(
        id='ns-001',
        agent_id='memory-test-agent',
        name='default',
    )

    # Mock embedding service.
    embedding_service = mock.Mock(spec=EmbeddingService)
    embedding_service.embed_text.return_value = [0.1, 0.2, 0.3]
    embedding_service.get_model_name.return_value = 'text-embedding-3-small'

    # Patch GraphBuilder to avoid real LangGraph construction.
    mock_graph = mock.Mock()
    mock_graph.invoke.return_value = {
        'messages': [mock.Mock(content='I remember you!')]
    }

    with mock.patch.object(GraphBuilder, 'build', return_value=mock_graph) as mock_build:
        with mock.patch.object(GraphBuilder, 'load_tools', return_value=[]):

            result = DomainEvent.handle(
                SendMessage,
                dependencies={
                    'agent_service': agent_service,
                    'conversation_service': conversation_service,
                    'llm_provider_service': llm_service,
                    'memory_service': memory_service,
                    'embedding_service': embedding_service,
                },
                agent_id='memory-test-agent',
                message='Hello, remember me?',
            )

    # Assert the response was produced.
    assert result is not None
    assert result.content == 'I remember you!'
    assert result.role == 'ai'

    # Assert the namespace was created on first message.
    memory_service.get_or_create_namespace.assert_called_once_with(
        agent_id='memory-test-agent',
        name='default',
    )

    # Assert memory tools were added to the graph build.
    build_call = mock_build.call_args
    tools_passed = build_call.kwargs.get('tools') or build_call[1].get('tools', [])
    # Memory tools (recall_memory, store_memory) should be in the list.
    assert len(tools_passed) == 2
    tool_names = [getattr(t, 'name', '') for t in tools_passed]
    assert 'recall_memory' in tool_names
    assert 'store_memory' in tool_names

    # Assert conversation was persisted with both messages.
    conversation_service.save.assert_called_once()
    saved_conversation = conversation_service.save.call_args[0][0]
    assert len(saved_conversation.messages) == 2
