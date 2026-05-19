"""tiferet_agents Utils Retry"""

# *** imports

# ** core
import time
from typing import Any, Callable

# ** app
from tiferet.events import RaiseError

from ..assets import constants as const

# *** utils

# ** util: retry_handler
class RetryHandler:
    '''
    Utility for executing callables with exponential backoff on transient errors.

    Catches provider-specific rate limit, timeout, and context length errors,
    maps them to structured TiferetError codes, and retries with configurable
    backoff and maximum attempts.
    '''

    # * method: execute_with_retry (static)
    @staticmethod
    def execute_with_retry(
            fn: Callable,
            max_retries: int = 3,
            base_delay: float = 1.0,
            max_delay: float = 60.0,
        ) -> Any:
        '''
        Execute a callable with exponential backoff on transient errors.

        :param fn: The callable to execute (no arguments).
        :type fn: Callable
        :param max_retries: Maximum number of retry attempts.
        :type max_retries: int
        :param base_delay: Base delay in seconds for exponential backoff.
        :type base_delay: float
        :param max_delay: Maximum delay cap in seconds.
        :type max_delay: float
        :return: The result of the callable.
        :rtype: Any
        '''

        for attempt in range(max_retries + 1):

            try:

                # Attempt the call.
                return fn()

            except Exception as e:

                # Classify the error.
                error_code = RetryHandler._classify_error(e)

                # Non-retryable errors are raised immediately.
                if error_code in (const.LLM_AUTH_ERROR_ID, const.LLM_CONTEXT_LENGTH_ERROR_ID, const.LLM_QUOTA_EXCEEDED_ID):
                    RaiseError.execute(
                        error_code=error_code,
                        error=str(e),
                    )

                # Retryable errors: back off if retries remain.
                if attempt < max_retries:
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    time.sleep(delay)
                    continue

                # Exhausted retries: raise the classified error.
                RaiseError.execute(
                    error_code=error_code,
                    error=str(e),
                )

    # * method: _classify_error (static)
    @staticmethod
    def _classify_error(error: Exception) -> str:
        '''
        Classify an exception into a structured error code.

        :param error: The exception to classify.
        :type error: Exception
        :return: The error code constant.
        :rtype: str
        '''

        error_str = str(type(error).__name__).lower()
        error_msg = str(error).lower()

        # Quota exhaustion errors (non-retryable billing errors).
        if 'insufficient_quota' in error_msg or 'exceeded your current quota' in error_msg:
            return const.LLM_QUOTA_EXCEEDED_ID

        # Rate limit errors.
        if 'ratelimit' in error_str or 'rate_limit' in error_msg or '429' in error_msg:
            return const.LLM_RATE_LIMIT_ERROR_ID

        # Context length / token overflow errors.
        if 'context_length' in error_msg or 'token' in error_msg and 'exceed' in error_msg:
            return const.LLM_CONTEXT_LENGTH_ERROR_ID

        # Authentication errors.
        if 'auth' in error_str or 'unauthorized' in error_msg or '401' in error_msg or '403' in error_msg:
            return const.LLM_AUTH_ERROR_ID

        # Timeout errors.
        if 'timeout' in error_str or 'timed out' in error_msg:
            return const.LLM_TIMEOUT_ERROR_ID

        # Default: generic invocation error.
        return const.LLM_INVOCATION_ERROR_ID
