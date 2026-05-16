"""tiferet_agents Integration Tests — SendMessage"""

# *** imports

# ** infra
import pytest
from pathlib import Path
from unittest import mock

# ** app
from tiferet.events import DomainEvent
from tiferet.assets.exceptions import TiferetError

from ..events.conversation import SendMessage
from ..interfaces.agent import AgentService
from ..interfaces.conversation import ConversationService
from ..interfaces.llm import LLMProviderService
from ..mappers.agent import AgentConfigurationAggregate
from ..mappers.conversation import ConversationAggregate, MessageAggregate
from ..utils.graph import GraphBuilder

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
