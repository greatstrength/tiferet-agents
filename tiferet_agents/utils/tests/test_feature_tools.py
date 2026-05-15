"""tiferet_agents Feature Tools Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ..feature_tools import create_feature_tool

# *** tests

# ** test: create_feature_tool_basic
def test_create_feature_tool_basic():
    '''
    Test that create_feature_tool returns a tool with the right name.
    '''

    # Arrange: mock app instance.
    mock_app = mock.Mock()
    mock_app.run.return_value = 42

    # Execute.
    tool = create_feature_tool(
        interface_id='basic_calc',
        feature_id='calc.add',
        app_instance=mock_app,
    )

    # Assert the tool has the right name.
    assert tool.name == 'calc_add'
    assert hasattr(tool, 'invoke')


# ** test: create_feature_tool_invocation
def test_create_feature_tool_invocation():
    '''
    Test that invoking the tool calls App.run with correct arguments.
    '''

    # Arrange.
    mock_app = mock.Mock()
    mock_app.run.return_value = 'result_value'

    tool = create_feature_tool(
        interface_id='basic_calc',
        feature_id='calc.add',
        tool_name='add_numbers',
        tool_description='Adds two numbers',
        app_instance=mock_app,
    )

    # Execute: invoke the tool with JSON data string.
    result = tool.invoke({'data': '{"a": "1", "b": "2"}'})

    # Assert App.run was called correctly.
    mock_app.run.assert_called_once_with('basic_calc', 'calc.add', data={'a': '1', 'b': '2'})
    assert result == 'result_value'


# ** test: create_feature_tool_custom_name
def test_create_feature_tool_custom_name():
    '''
    Test custom tool name and description.
    '''

    # Arrange.
    mock_app = mock.Mock()

    tool = create_feature_tool(
        interface_id='sci_calc',
        feature_id='calc.sqrt',
        tool_name='square_root',
        tool_description='Calculate the square root',
        app_instance=mock_app,
    )

    # Assert.
    assert tool.name == 'square_root'
    assert 'square root' in tool.description.lower()


# ** test: create_feature_tool_default_name
def test_create_feature_tool_default_name():
    '''
    Test that default name replaces dots with underscores.
    '''

    # Arrange.
    mock_app = mock.Mock()

    tool = create_feature_tool(
        interface_id='basic_calc',
        feature_id='calc.multiply',
        app_instance=mock_app,
    )

    # Assert.
    assert tool.name == 'calc_multiply'
