"""tiferet_agents Interfaces LLM"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Any

# ** app
from tiferet.interfaces import Service

# *** interfaces

# ** interface: llm_provider_service
class LLMProviderService(Service):
    '''
    Service interface for creating LLM provider instances.

    Abstracts the construction of LangChain-compatible chat models
    from provider name + model name + configuration parameters.
    '''

    # * method: create_model
    @abstractmethod
    def create_model(self,
            provider: str,
            model: str,
            temperature: float = 0.7,
            max_tokens: int | None = None,
            **kwargs,
        ) -> Any:
        '''
        Create and return a LangChain-compatible chat model.

        :param provider: The LLM provider name (e.g., 'openai', 'anthropic').
        :type provider: str
        :param model: The model identifier (e.g., 'gpt-4o-mini').
        :type model: str
        :param temperature: Sampling temperature.
        :type temperature: float
        :param max_tokens: Maximum tokens in the response.
        :type max_tokens: int | None
        :param kwargs: Additional provider-specific parameters.
        :type kwargs: dict
        :return: A LangChain-compatible chat model instance.
        :rtype: Any
        '''
        raise NotImplementedError()
