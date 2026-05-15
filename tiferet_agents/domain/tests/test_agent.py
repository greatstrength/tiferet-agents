"""tiferet_agents Agent Domain Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..agent import AgentConfiguration, AgentTool

# *** tests

# ** test: agent_tool_creation
def test_agent_tool_creation():
    '''
    Test creating an AgentTool with required fields.
    '''

    # Create a tool with explicit values.
    tool = AgentTool(
        id='calc_tool',
        name='Calculator',
        description='Performs math',
        module_path='tools.calc',
        class_name='Calculator',
    )

    # Assert all fields are set.
    assert tool.id == 'calc_tool'
    assert tool.name == 'Calculator'
    assert tool.module_path == 'tools.calc'
    assert tool.parameters == {}


# ** test: agent_configuration_defaults
def test_agent_configuration_defaults():
    '''
    Test that AgentConfiguration auto-derives id and timestamps.
    '''

    # Create with only the required name field.
    agent = AgentConfiguration(name='Test Agent')

    # Assert defaults are applied.
    assert agent.id  # UUID was generated
    assert agent.name == 'Test Agent'
    assert agent.provider == 'openai'
    assert agent.model == 'gpt-4o-mini'
    assert agent.temperature == 0.7
    assert agent.max_tokens is None
    assert agent.tools == []
    assert agent.created_at
    assert agent.updated_at


# ** test: agent_configuration_explicit_id
def test_agent_configuration_explicit_id():
    '''
    Test creating an AgentConfiguration with an explicit ID.
    '''

    # Create with explicit id.
    agent = AgentConfiguration(id='my_agent', name='My Agent')

    # Assert the explicit ID was used.
    assert agent.id == 'my_agent'


# ** test: agent_configuration_with_tools
def test_agent_configuration_with_tools():
    '''
    Test creating an AgentConfiguration with nested tools.
    '''

    # Create with tools.
    agent = AgentConfiguration(
        name='Tooled Agent',
        tools=[
            AgentTool(
                id='t1',
                name='Tool One',
                module_path='tools.one',
                class_name='ToolOne',
            ),
        ],
    )

    # Assert tools are present.
    assert len(agent.tools) == 1
    assert agent.tools[0].id == 't1'


# ** test: agent_configuration_get_tool
def test_agent_configuration_get_tool():
    '''
    Test the get_tool method.
    '''

    # Create with a tool.
    agent = AgentConfiguration(
        name='Agent',
        tools=[
            AgentTool(id='t1', name='T1', module_path='m', class_name='C'),
        ],
    )

    # Assert get_tool works.
    assert agent.get_tool('t1') is not None
    assert agent.get_tool('nonexistent') is None
