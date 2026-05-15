"""tiferet_agents Utils Embeddings"""

# *** imports

# ** core
from typing import Any, List

# ** app
from tiferet.events import RaiseError

from ..assets import constants as const
from ..interfaces.embedding import EmbeddingService

# *** utils

# ** util: embedding_provider_factory
class EmbeddingProviderFactory(EmbeddingService):
    '''
    Factory utility for creating and using LangChain-compatible embedding models.

    Supports OpenAI out of the box; additional providers use lazy imports.
    '''

    # * attribute: _model
    _model: Any

    # * attribute: _model_name
    _model_name: str

    # * init
    def __init__(self, provider: str = 'openai', model: str = 'text-embedding-3-small', **kwargs):
        '''
        Initialize the embedding provider factory.

        :param provider: The embedding provider name (e.g., openai).
        :type provider: str
        :param model: The embedding model identifier.
        :type model: str
        :param kwargs: Additional provider-specific parameters.
        :type kwargs: dict
        '''

        # Store the model name.
        self._model_name = model

        # Dispatch to the appropriate provider.
        if provider == 'openai':
            self._model = self._create_openai(model=model, **kwargs)
        elif provider == 'google':
            self._model = self._create_google(model=model, **kwargs)
        else:
            RaiseError.execute(
                error_code=const.INVALID_PROVIDER_ID,
                provider=provider,
            )

    # * method: embed_text
    def embed_text(self, text: str) -> List[float]:
        '''
        Generate an embedding vector for a single text.

        :param text: The text to embed.
        :type text: str
        :return: The embedding vector.
        :rtype: List[float]
        '''

        try:

            # Delegate to the LangChain embedding model.
            return self._model.embed_query(text)

        except Exception as e:

            # Wrap embedding errors.
            RaiseError.execute(
                error_code=const.EMBEDDING_ERROR_ID,
                error=str(e),
            )

    # * method: embed_texts
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        '''
        Generate embedding vectors for multiple texts.

        :param texts: The texts to embed.
        :type texts: List[str]
        :return: A list of embedding vectors.
        :rtype: List[List[float]]
        '''

        try:

            # Delegate to the LangChain embedding model.
            return self._model.embed_documents(texts)

        except Exception as e:

            # Wrap embedding errors.
            RaiseError.execute(
                error_code=const.EMBEDDING_ERROR_ID,
                error=str(e),
            )

    # * method: get_model_name
    def get_model_name(self) -> str:
        '''
        Return the name of the embedding model.

        :return: The model name.
        :rtype: str
        '''

        # Return the stored model name.
        return self._model_name

    # * method: _create_openai
    def _create_openai(self, model: str, **kwargs) -> Any:
        '''
        Create an OpenAI embedding model.

        :param model: The model identifier.
        :type model: str
        :param kwargs: Additional parameters.
        :type kwargs: dict
        :return: An OpenAIEmbeddings instance.
        :rtype: Any
        '''

        # Import and instantiate OpenAIEmbeddings.
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=model, **kwargs)

    # * method: _create_google
    def _create_google(self, model: str, **kwargs) -> Any:
        '''
        Create a Google embedding model.

        :param model: The model identifier.
        :type model: str
        :param kwargs: Additional parameters.
        :type kwargs: dict
        :return: A GoogleGenerativeAIEmbeddings instance.
        :rtype: Any
        '''

        # Import and instantiate (optional dependency).
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            return GoogleGenerativeAIEmbeddings(model=model, **kwargs)
        except ImportError:
            RaiseError.execute(
                error_code=const.INVALID_PROVIDER_ID,
                provider='google',
                message='langchain-google-genai is not installed. Install with: pip install tiferet-agents[google]',
            )
