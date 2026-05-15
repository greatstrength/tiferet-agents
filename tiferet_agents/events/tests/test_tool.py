"""tiferet_agents Tool Event Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events import DomainEvent
from tiferet.assets.exceptions import TiferetError

from ..tool import RegisterTool, ListTools, RemoveTool
from ...interfaces.agent import AgentService
from ...mappers.agent import AgentConfigurationAggregate, AgentToolAggregate

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
    Sample agent aggregate with no tools.
    '''
    return AgentConfigurationAggregate(
        id='test-agent',
        name='Test Agent',
        provider='openai',
        model='gpt-4o-mini',
    )

# ** fixture: sample_agent_with_tool
@pytest.fixture
def sample_agent_with_tool():
    '''
    Sample agent aggregate with one tool.
    '''
    agent = AgentConfigurationAggregate(
        id='test-agent',
        name='Test Agent',
        provider='openai',
        model='gpt-4o-mini',
    )
    tool = AgentToolAggregate(
        id='existing_tool',
        name='Existing Tool',
        module_path='some.module',
        class_name='SomeTool',
    )
    agent.add_tool(tool)
    return agent

# *** tests

# ** test: register_tool_success
def test_register_tool_success(mock_agent_service, sample_agent):
    '''
    Test successful tool registration on an agent.
    '''

    # Arrange: agent exists.
    mock_agent_service.get.return_value = sample_agent

    # Execute.
    result = DomainEvent.handle(
        RegisterTool,
        dependencies={'agent_service': mock_agent_service},
        agent_id='test-agent',
        tool_id='calc_tool',
        name='Calculator',
        module_path='tools.calc',
        class_name='Calculator',
        description='Performs math operations',
    )

    # Assert the tool was created and agent saved.
    assert result.id == 'calc_tool'
    assert result.name == 'Calculator'
    assert result.module_path == 'tools.calc'
    mock_agent_service.save.assert_called_once()


# ** test: register_tool_agent_not_found
def test_register_tool_agent_not_found(mock_agent_service):
    '''
    Test that registering a tool on a nonexistent agent raises an error.
    '''

    # Arrange: agent does not exist.
    mock_agent_service.get.return_value = None

    # Execute and expect error.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            RegisterTool,
            dependencies={'agent_service': mock_agent_service},
            agent_id='nonexistent',
            tool_id='calc_tool',
            name='Calculator',
            module_path='tools.calc',
            class_name='Calculator',
        )


# ** test: register_tool_duplicate
def test_register_tool_duplicate(mock_agent_service, sample_agent_with_tool):
    '''
    Test that registering a duplicate tool raises an error.
    '''

    # Arrange: agent exists with a tool.
    mock_agent_service.get.return_value = sample_agent_with_tool

    # Execute and expect error for duplicate tool ID.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            RegisterTool,
            dependencies={'agent_service': mock_agent_service},
            agent_id='test-agent',
            tool_id='existing_tool',
            name='Duplicate Tool',
            module_path='some.module',
            class_name='SomeTool',
        )


# ** test: list_tools_success
def test_list_tools_success(mock_agent_service, sample_agent_with_tool):
    '''
    Test successful listing of agent tools.
    '''

    # Arrange.
    mock_agent_service.get.return_value = sample_agent_with_tool

    # Execute.
    result = DomainEvent.handle(
        ListTools,
        dependencies={'agent_service': mock_agent_service},
        agent_id='test-agent',
    )

    # Assert.
    assert len(result) == 1
    assert result[0].id == 'existing_tool'


# ** test: list_tools_empty
def test_list_tools_empty(mock_agent_service, sample_agent):
    '''
    Test listing tools for an agent with no tools.
    '''

    # Arrange.
    mock_agent_service.get.return_value = sample_agent

    # Execute.
    result = DomainEvent.handle(
        ListTools,
        dependencies={'agent_service': mock_agent_service},
        agent_id='test-agent',
    )

    # Assert.
    assert result == []


# ** test: list_tools_agent_not_found
def test_list_tools_agent_not_found(mock_agent_service):
    '''
    Test that listing tools for a nonexistent agent raises an error.
    '''

    # Arrange.
    mock_agent_service.get.return_value = None

    # Execute and expect error.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            ListTools,
            dependencies={'agent_service': mock_agent_service},
            agent_id='nonexistent',
        )


# ** test: remove_tool_success
def test_remove_tool_success(mock_agent_service, sample_agent_with_tool):
    '''
    Test successful tool removal.
    '''

    # Arrange.
    mock_agent_service.get.return_value = sample_agent_with_tool

    # Execute.
    DomainEvent.handle(
        RemoveTool,
        dependencies={'agent_service': mock_agent_service},
        agent_id='test-agent',
        tool_id='existing_tool',
    )

    # Assert the agent was saved after removal.
    mock_agent_service.save.assert_called_once()
    # Verify tool was removed from the agent.
    assert len(sample_agent_with_tool.tools) == 0


# ** test: remove_tool_not_found
def test_remove_tool_not_found(mock_agent_service, sample_agent):
    '''
    Test that removing a nonexistent tool raises an error.
    '''

    # Arrange: agent exists but tool does not.
    mock_agent_service.get.return_value = sample_agent

    # Execute and expect error.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            RemoveTool,
            dependencies={'agent_service': mock_agent_service},
            agent_id='test-agent',
            tool_id='nonexistent_tool',
        )


# ** test: remove_tool_agent_not_found
def test_remove_tool_agent_not_found(mock_agent_service):
    '''
    Test that removing a tool from a nonexistent agent raises an error.
    '''

    # Arrange.
    mock_agent_service.get.return_value = None

    # Execute and expect error.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            RemoveTool,
            dependencies={'agent_service': mock_agent_service},
            agent_id='nonexistent',
            tool_id='some_tool',
        )
