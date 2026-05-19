"""tiferet_agents GraphBuilder Tool Loading Tests"""

# *** imports

# ** core
import sys
import types
from unittest import mock

# ** infra
import pytest

from langchain_core.tools import tool, BaseTool

# ** app
from tiferet.assets.exceptions import TiferetError

from ...assets import constants as const
from ..graph import GraphBuilder

# *** fixtures

# ** fixture: make_agent_config
@pytest.fixture
def make_agent_config():
    '''
    Factory fixture for creating mock AgentConfigurationAggregate objects.
    '''

    def _make(tool_defs):
        config = mock.Mock()
        config.tools = tool_defs
        return config

    return _make


# ** fixture: make_tool_def
@pytest.fixture
def make_tool_def():
    '''
    Factory fixture for creating mock tool definition objects.
    '''

    def _make(module_path, class_name, parameters=None, tool_id='test_tool'):
        td = mock.Mock()
        td.id = tool_id
        td.module_path = module_path
        td.class_name = class_name
        td.parameters = parameters
        return td

    return _make


# *** tests

# ** test: load_tools_prebuilt_decorator_tool
def test_load_tools_prebuilt_decorator_tool(make_agent_config, make_tool_def):
    '''
    Test that a @tool-decorated pre-built tool object loads without instantiation.
    '''

    # Create a @tool-decorated function in a temporary module.
    @tool
    def my_search(query: str) -> str:
        '''Search for something.'''
        return f'result: {query}'

    # Register as a module-level attribute.
    temp_module = types.ModuleType('_test_tools_prebuilt')
    temp_module.my_search = my_search
    sys.modules['_test_tools_prebuilt'] = temp_module

    try:
        # Build agent config referencing the pre-built tool.
        tool_def = make_tool_def('_test_tools_prebuilt', 'my_search')
        config = make_agent_config([tool_def])

        # Load the tools.
        result = GraphBuilder.load_tools(config)

        # Assert the tool was loaded as-is (same object).
        assert len(result) == 1
        assert result[0] is my_search
        assert result[0].name == 'my_search'

    finally:
        del sys.modules['_test_tools_prebuilt']


# ** test: load_tools_prebuilt_with_params
def test_load_tools_prebuilt_with_params(make_agent_config, make_tool_def):
    '''
    Test that static parameters are bound to a pre-built tool object.
    '''

    # Create a @tool-decorated function.
    @tool
    def my_tool(query: str) -> str:
        '''A tool.'''
        return query

    # Register in temp module.
    temp_module = types.ModuleType('_test_tools_params')
    temp_module.my_tool = my_tool
    sys.modules['_test_tools_params'] = temp_module

    try:
        # Build config with static parameters.
        tool_def = make_tool_def(
            '_test_tools_params', 'my_tool',
            parameters={'api_key': 'test123'},
        )
        config = make_agent_config([tool_def])

        # Load the tools.
        result = GraphBuilder.load_tools(config)

        # Assert parameters were bound.
        assert len(result) == 1
        assert result[0].api_key == 'test123'
        # Verify name and description are preserved.
        assert result[0].name == 'my_tool'
        assert result[0].description == 'A tool.'

    finally:
        del sys.modules['_test_tools_params']


# ** test: load_tools_constructor_class
def test_load_tools_constructor_class(make_agent_config, make_tool_def):
    '''
    Test that a constructor-based tool class is instantiated correctly.
    '''

    # Create a simple class in a temp module.
    class MyToolClass:
        def __init__(self, api_key='default'):
            self.api_key = api_key

    temp_module = types.ModuleType('_test_tools_class')
    temp_module.MyToolClass = MyToolClass
    sys.modules['_test_tools_class'] = temp_module

    try:
        # Without parameters.
        tool_def = make_tool_def('_test_tools_class', 'MyToolClass')
        config = make_agent_config([tool_def])
        result = GraphBuilder.load_tools(config)
        assert len(result) == 1
        assert isinstance(result[0], MyToolClass)
        assert result[0].api_key == 'default'

        # With parameters.
        tool_def = make_tool_def(
            '_test_tools_class', 'MyToolClass',
            parameters={'api_key': 'custom'},
        )
        config = make_agent_config([tool_def])
        result = GraphBuilder.load_tools(config)
        assert len(result) == 1
        assert result[0].api_key == 'custom'

    finally:
        del sys.modules['_test_tools_class']


# ** test: load_tools_empty_config
def test_load_tools_empty_config(make_agent_config):
    '''
    Test that empty tool config returns an empty list.
    '''

    config = make_agent_config([])
    assert GraphBuilder.load_tools(config) == []

    config = make_agent_config(None)
    assert GraphBuilder.load_tools(config) == []


# ** test: load_tools_import_error
def test_load_tools_import_error(make_agent_config, make_tool_def):
    '''
    Test that import failures produce a structured TOOL_LOAD_ERROR.
    '''

    tool_def = make_tool_def('nonexistent.module', 'SomeTool')
    config = make_agent_config([tool_def])

    with pytest.raises(TiferetError) as exc_info:
        GraphBuilder.load_tools(config)

    assert exc_info.value.error_code == const.TOOL_LOAD_ERROR_ID


# ** test: is_tool_instance_detection
def test_is_tool_instance_detection():
    '''
    Test that _is_tool_instance correctly detects tool instances vs classes.
    '''

    # A @tool-decorated function should be detected.
    @tool
    def sample(query: str) -> str:
        '''Sample.'''
        return query

    assert GraphBuilder._is_tool_instance(sample) is True

    # A plain class should not be detected.
    class PlainClass:
        pass

    assert GraphBuilder._is_tool_instance(PlainClass) is False

    # A plain string should not be detected.
    assert GraphBuilder._is_tool_instance('not_a_tool') is False
