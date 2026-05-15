"""tiferet_agents PromptRenderer Tests"""

# *** imports

# ** infra
import pytest
from datetime import datetime, timezone
from unittest import mock

# ** app
from ..prompts import PromptRenderer, SafeDict

# *** tests

# ** test: safe_dict_missing_key
def test_safe_dict_missing_key():
    '''
    Test that SafeDict returns placeholder for missing keys.
    '''

    # Create a SafeDict and access a missing key.
    d = SafeDict(a='1')

    # Assert missing key returns placeholder.
    assert d['a'] == '1'
    assert '{missing}'.format_map(d) == '{missing}'


# ** test: render_no_variables
def test_render_no_variables():
    '''
    Test rendering a template with no variables.
    '''

    # Render a plain string.
    result = PromptRenderer.render('You are a helpful assistant.')

    # Assert unchanged.
    assert result == 'You are a helpful assistant.'


# ** test: render_with_context
def test_render_with_context():
    '''
    Test rendering a template with user-supplied context.
    '''

    # Render with context variables.
    template = 'You are {agent_name}, a {role} assistant.'
    result = PromptRenderer.render(template, {'agent_name': 'Tiferet Bot', 'role': 'coding'})

    # Assert variables were substituted.
    assert result == 'You are Tiferet Bot, a coding assistant.'


# ** test: render_builtin_current_date
def test_render_builtin_current_date():
    '''
    Test that the built-in {current_date} variable is available.
    '''

    # Render with current_date.
    template = 'Today is {current_date}.'
    result = PromptRenderer.render(template)

    # Assert it contains a date-like string.
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    assert result == f'Today is {today}.'


# ** test: render_missing_variable_preserved
def test_render_missing_variable_preserved():
    '''
    Test that missing variables are preserved as placeholders.
    '''

    # Render with an undefined variable.
    template = 'Hello {user_name}, your ID is {user_id}.'
    result = PromptRenderer.render(template, {'user_name': 'Alice'})

    # Assert the missing variable is preserved.
    assert result == 'Hello Alice, your ID is {user_id}.'


# ** test: render_context_overrides_builtin
def test_render_context_overrides_builtin():
    '''
    Test that user context can override built-in variables.
    '''

    # Override current_date.
    template = 'Date: {current_date}'
    result = PromptRenderer.render(template, {'current_date': '2025-01-01'})

    # Assert the override took effect.
    assert result == 'Date: 2025-01-01'


# ** test: render_none_context
def test_render_none_context():
    '''
    Test rendering with None context uses built-ins only.
    '''

    # Render with None context.
    template = 'Today is {current_date}. Hello {name}.'
    result = PromptRenderer.render(template, None)

    # Assert current_date is filled and name is preserved.
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    assert result == f'Today is {today}. Hello {{name}}.'
