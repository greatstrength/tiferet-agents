"""tiferet_agents Utils Feature Tools"""

# *** imports

# ** core
from typing import Any

# ** infra
from langchain_core.tools import tool

# *** utils

# ** util: create_feature_tool
def create_feature_tool(
        interface_id: str,
        feature_id: str,
        tool_name: str | None = None,
        tool_description: str | None = None,
        app_instance: Any = None,
    ) -> Any:
    '''
    Create a LangChain tool that invokes a Tiferet feature.

    Wraps App.run(interface_id, feature_id, data=kwargs) as a @tool-decorated
    function, enabling agents to invoke Tiferet features as tools.

    :param interface_id: The Tiferet interface identifier.
    :type interface_id: str
    :param feature_id: The Tiferet feature identifier.
    :type feature_id: str
    :param tool_name: Optional custom tool name (defaults to feature_id).
    :type tool_name: str | None
    :param tool_description: Optional custom description.
    :type tool_description: str | None
    :param app_instance: Optional pre-initialized App instance.
    :type app_instance: Any
    :return: A LangChain tool callable.
    :rtype: Any
    '''

    # Resolve the app instance lazily if not provided.
    _app = app_instance

    # Build the tool name and description.
    name = tool_name or feature_id.replace('.', '_')
    description = tool_description or f'Execute Tiferet feature: {feature_id}'

    @tool(name, description=description)
    def feature_tool(data: str = '{}') -> str:
        '''Execute a Tiferet feature with the provided arguments as a JSON string.'''

        # Lazy import to avoid circular dependencies.
        nonlocal _app
        if _app is None:
            from tiferet import App
            _app = App()

        # Parse data from JSON string.
        import json
        try:
            parsed_data = json.loads(data) if isinstance(data, str) else data
        except (json.JSONDecodeError, TypeError):
            parsed_data = {}

        # Run the feature and return the result as a string.
        result = _app.run(interface_id, feature_id, data=parsed_data)
        return str(result)

    # Return the tool.
    return feature_tool
