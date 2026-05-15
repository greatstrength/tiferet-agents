"""tiferet_agents Approval Event Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events import DomainEvent
from tiferet.assets.exceptions import TiferetError

from ..approval import ApproveToolCall, DenyToolCall
from ...interfaces.agent import AgentService
from ...interfaces.llm import LLMProviderService
from ...mappers.agent import AgentConfigurationAggregate
from ...utils.graph import GraphBuilder

# *** fixtures

# ** fixture: mock_agent_service
@pytest.fixture
def mock_agent_service():
    '''
    Mock AgentService for testing.
    '''
    return mock.Mock(spec=AgentService)

# ** fixture: mock_llm_service
@pytest.fixture
def mock_llm_service():
    '''
    Mock LLMProviderService for testing.
    '''
    return mock.Mock(spec=LLMProviderService)

# ** fixture: sample_agent
@pytest.fixture
def sample_agent():
    '''
    Sample agent aggregate for testing.
    '''
    return AgentConfigurationAggregate(
        id='test-agent',
        name='Test Agent',
        provider='openai',
        model='gpt-4o-mini',
    )

# ** fixture: mock_graph
@pytest.fixture
def mock_graph():
    '''
    Mock compiled graph for testing.
    '''
    graph = mock.Mock()
    graph.invoke.return_value = {
        'messages': [mock.Mock(content='Tool result')]
    }
    return graph

# *** tests

# ** test: approve_tool_call_success
def test_approve_tool_call_success(mock_agent_service, mock_llm_service, sample_agent, mock_graph):
    '''
    Test successful approval of a pending tool call.
    '''

    # Arrange: agent exists.
    mock_agent_service.get.return_value = sample_agent

    # Patch GraphBuilder.resume to avoid real graph interaction.
    with mock.patch.object(GraphBuilder, 'resume', return_value={'messages': [mock.Mock(content='Approved result')]}) as mock_resume:

        # Execute.
        result = DomainEvent.handle(
            ApproveToolCall,
            dependencies={
                'agent_service': mock_agent_service,
                'llm_provider_service': mock_llm_service,
            },
            agent_id='test-agent',
            thread_id='thread-123',
            graph=mock_graph,
        )

        # Assert resume was called with approve=True.
        mock_resume.assert_called_once_with(
            graph=mock_graph,
            thread_id='thread-123',
            approve=True,
        )
        assert result is not None


# ** test: approve_tool_call_agent_not_found
def test_approve_tool_call_agent_not_found(mock_agent_service, mock_llm_service, mock_graph):
    '''
    Test that approving on a nonexistent agent raises an error.
    '''

    # Arrange.
    mock_agent_service.get.return_value = None

    # Execute and expect error.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            ApproveToolCall,
            dependencies={
                'agent_service': mock_agent_service,
                'llm_provider_service': mock_llm_service,
            },
            agent_id='nonexistent',
            thread_id='thread-123',
            graph=mock_graph,
        )


# ** test: deny_tool_call_success
def test_deny_tool_call_success(mock_agent_service, mock_llm_service, sample_agent, mock_graph):
    '''
    Test successful denial of a pending tool call.
    '''

    # Arrange: agent exists.
    mock_agent_service.get.return_value = sample_agent

    # Patch GraphBuilder.resume.
    with mock.patch.object(GraphBuilder, 'resume', return_value={'messages': [mock.Mock(content='Denied')]}) as mock_resume:

        # Execute.
        result = DomainEvent.handle(
            DenyToolCall,
            dependencies={
                'agent_service': mock_agent_service,
                'llm_provider_service': mock_llm_service,
            },
            agent_id='test-agent',
            thread_id='thread-123',
            graph=mock_graph,
        )

        # Assert resume was called with approve=False.
        mock_resume.assert_called_once_with(
            graph=mock_graph,
            thread_id='thread-123',
            approve=False,
        )
        assert result is not None


# ** test: deny_tool_call_agent_not_found
def test_deny_tool_call_agent_not_found(mock_agent_service, mock_llm_service, mock_graph):
    '''
    Test that denying on a nonexistent agent raises an error.
    '''

    # Arrange.
    mock_agent_service.get.return_value = None

    # Execute and expect error.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            DenyToolCall,
            dependencies={
                'agent_service': mock_agent_service,
                'llm_provider_service': mock_llm_service,
            },
            agent_id='nonexistent',
            thread_id='thread-123',
            graph=mock_graph,
        )
