"""tiferet_agents Agent Event Tests"""

# *** imports

# ** infra
from unittest import mock

import pytest
from tiferet.assets.exceptions import TiferetError

# ** app
from tiferet.events import DomainEvent

from ...interfaces.agent import AgentService
from ...mappers.agent import AgentConfigurationAggregate
from ..agent import ConfigureAgent, GetAgent, ListAgents, RemoveAgent

# *** fixtures

# ** fixture: mock_agent_service
@pytest.fixture
def mock_agent_service():
    '''
    Mock AgentService for testing.
    '''
    return mock.Mock(spec=AgentService)

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

# *** tests

# ** test: configure_agent_success
def test_configure_agent_success(mock_agent_service):
    '''
    Test successful agent configuration creation.
    '''

    # Arrange: agent does not exist.
    mock_agent_service.exists.return_value = False

    # Execute.
    result = DomainEvent.handle(
        ConfigureAgent,
        dependencies={'agent_service': mock_agent_service},
        name='New Agent',
        provider='openai',
        model='gpt-4o-mini',
    )

    # Assert agent was created and saved.
    assert result.name == 'New Agent'
    assert result.provider == 'openai'
    mock_agent_service.save.assert_called_once()


# ** test: configure_agent_duplicate
def test_configure_agent_duplicate(mock_agent_service):
    '''
    Test that configuring a duplicate agent raises an error.
    '''

    # Arrange: agent already exists.
    mock_agent_service.exists.return_value = True

    # Execute and expect error.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            ConfigureAgent,
            dependencies={'agent_service': mock_agent_service},
            name='Duplicate Agent',
            id='existing-id',
        )


# ** test: get_agent_success
def test_get_agent_success(mock_agent_service, sample_agent):
    '''
    Test successful agent retrieval.
    '''

    # Arrange.
    mock_agent_service.get.return_value = sample_agent

    # Execute.
    result = DomainEvent.handle(
        GetAgent,
        dependencies={'agent_service': mock_agent_service},
        id='test-agent',
    )

    # Assert.
    assert result is sample_agent
    mock_agent_service.get.assert_called_once_with('test-agent')


# ** test: get_agent_not_found
def test_get_agent_not_found(mock_agent_service):
    '''
    Test that getting a nonexistent agent raises an error.
    '''

    # Arrange.
    mock_agent_service.get.return_value = None

    # Execute and expect error.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            GetAgent,
            dependencies={'agent_service': mock_agent_service},
            id='nonexistent',
        )


# ** test: list_agents
def test_list_agents(mock_agent_service, sample_agent):
    '''
    Test listing all agents.
    '''

    # Arrange.
    mock_agent_service.list.return_value = [sample_agent]

    # Execute.
    result = DomainEvent.handle(
        ListAgents,
        dependencies={'agent_service': mock_agent_service},
    )

    # Assert.
    assert len(result) == 1
    assert result[0] is sample_agent


# ** test: remove_agent_success
def test_remove_agent_success(mock_agent_service):
    '''
    Test successful agent deletion.
    '''

    # Arrange.
    mock_agent_service.exists.return_value = True

    # Execute.
    DomainEvent.handle(
        RemoveAgent,
        dependencies={'agent_service': mock_agent_service},
        id='test-agent',
    )

    # Assert.
    mock_agent_service.delete.assert_called_once_with('test-agent')


# ** test: remove_agent_not_found
def test_remove_agent_not_found(mock_agent_service):
    '''
    Test that removing a nonexistent agent raises an error.
    '''

    # Arrange.
    mock_agent_service.exists.return_value = False

    # Execute and expect error.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            RemoveAgent,
            dependencies={'agent_service': mock_agent_service},
            id='nonexistent',
        )
