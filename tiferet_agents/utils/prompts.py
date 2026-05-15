"""tiferet_agents Utils Prompts"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import Any, Dict

# *** classes

# ** class: safe_dict
class SafeDict(dict):
    '''
    A dict subclass that returns the original placeholder for missing keys
    instead of raising KeyError when used with str.format_map.
    '''

    # * method: __missing__
    def __missing__(self, key: str) -> str:
        '''
        Return the key wrapped in braces for missing entries.

        :param key: The missing key.
        :type key: str
        :return: The key as an unresolved placeholder.
        :rtype: str
        '''

        # Return the key as a placeholder string.
        return '{' + key + '}'

# *** utils

# ** util: prompt_renderer
class PromptRenderer:
    '''
    Utility for rendering system prompt templates with context variables.

    Uses Python's str.format_map with SafeDict for safe interpolation.
    Missing variables are preserved as-is rather than raising errors.
    '''

    # * method: render (static)
    @staticmethod
    def render(template: str, context: Dict[str, Any] | None = None) -> str:
        '''
        Render a prompt template with the given context variables.

        Built-in variables (always available unless overridden):
        - {current_date}: Current UTC date in YYYY-MM-DD format.
        - {current_time}: Current UTC datetime in ISO 8601 format.

        :param template: The prompt template string with {variable} placeholders.
        :type template: str
        :param context: Optional dict of context variables to inject.
        :type context: Dict[str, Any] | None
        :return: The rendered prompt string.
        :rtype: str
        '''

        # Build the context with built-in defaults.
        now = datetime.now(timezone.utc)
        render_context = SafeDict(
            current_date=now.strftime('%Y-%m-%d'),
            current_time=now.isoformat(),
        )

        # Merge user-provided context (overrides built-ins).
        if context:
            render_context.update(context)

        # Render and return.
        return template.format_map(render_context)
