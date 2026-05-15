"""tiferet_agents Utils Providers"""

# *** imports

# ** core
from typing import Any

# ** app
from tiferet.events import RaiseError

from ..assets import constants as const
from ..interfaces.llm import LLMProviderService

# *** utils

# ** util: llm_provider_factory
class LLMProviderFactory(LLMProviderService):
    '''
    Factory utility for creating LangChain-compatible chat model instances.

    Supports OpenAI out of the box; additional providers can be added by
    extending the provider dispatch map.
    '''

    # * method: create_model
    def create_model(self,
            provider: str,
            model: str,
            temperature: float = 0.7,
            max_tokens: int | None = None,
            **kwargs,
        ) -> Any:
        '''
        Create and return a LangChain-compatible chat model.

        :param provider: The LLM provider name.
        :type provider: str
        :param model: The model identifier.
        :type model: str
        :param temperature: Sampling temperature.
        :type temperature: float
        :param max_tokens: Maximum response tokens.
        :type max_tokens: int | None
        :param kwargs: Additional provider-specific parameters.
        :type kwargs: dict
        :return: A LangChain chat model instance.
        :rtype: Any
        '''

        # Build common kwargs.
        model_kwargs = dict(
            model=model,
            temperature=temperature,
            **kwargs,
        )
        if max_tokens is not None:
            model_kwargs['max_tokens'] = max_tokens

        # Dispatch to the appropriate provider.
        if provider == 'openai':
            return self._create_openai(**model_kwargs)

        if provider == 'anthropic':
            return self._create_anthropic(**model_kwargs)

        # Raise an error for unsupported providers.
        RaiseError.execute(
            error_code=const.INVALID_PROVIDER_ID,
            provider=provider,
        )

    # * method: _create_openai
    def _create_openai(self, **kwargs) -> Any:
        '''
        Create an OpenAI chat model.

        :param kwargs: Model parameters.
        :type kwargs: dict
        :return: A ChatOpenAI instance.
        :rtype: Any
        '''

        # Import and instantiate ChatOpenAI.
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(**kwargs)

    # * method: _create_anthropic
    def _create_anthropic(self, **kwargs) -> Any:
        '''
        Create an Anthropic chat model.

        :param kwargs: Model parameters.
        :type kwargs: dict
        :return: A ChatAnthropic instance.
        :rtype: Any
        '''

        # Import and instantiate ChatAnthropic (optional dependency).
        try:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(**kwargs)
        except ImportError:
            RaiseError.execute(
                error_code=const.INVALID_PROVIDER_ID,
                provider='anthropic',
                message='langchain-anthropic is not installed. Install with: pip install tiferet-agents[anthropic]',
            )
