"""tiferet_agents RetryHandler Tests"""

# *** imports

# ** infra
from unittest import mock

import pytest

# ** app
from tiferet.assets.exceptions import TiferetError

from ...assets import constants as const
from ..retry import RetryHandler

# *** tests

# ** test: retry_handler_success_first_attempt
def test_retry_handler_success_first_attempt():
    '''
    Test that a successful call returns immediately without retry.
    '''

    # Arrange.
    fn = mock.Mock(return_value='success')

    # Execute.
    result = RetryHandler.execute_with_retry(fn, max_retries=3, base_delay=0.01)

    # Assert.
    assert result == 'success'
    fn.assert_called_once()


# ** test: retry_handler_success_after_retries
def test_retry_handler_success_after_retries():
    '''
    Test that a transient error is retried and succeeds.
    '''

    # Arrange: fail twice with a timeout, then succeed.
    fn = mock.Mock(side_effect=[
        TimeoutError('timed out'),
        TimeoutError('timed out'),
        'success',
    ])

    # Execute.
    result = RetryHandler.execute_with_retry(fn, max_retries=3, base_delay=0.01)

    # Assert.
    assert result == 'success'
    assert fn.call_count == 3


# ** test: retry_handler_exhausted_retries
def test_retry_handler_exhausted_retries():
    '''
    Test that exhausting retries raises a structured error.
    '''

    # Arrange: always fail with timeout.
    fn = mock.Mock(side_effect=TimeoutError('timed out'))

    # Execute and expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        RetryHandler.execute_with_retry(fn, max_retries=2, base_delay=0.01)

    # Assert all attempts were made (initial + 2 retries).
    assert fn.call_count == 3
    assert exc_info.value.error_code == const.LLM_TIMEOUT_ERROR_ID


# ** test: retry_handler_non_retryable_auth_error
def test_retry_handler_non_retryable_auth_error():
    '''
    Test that authentication errors are raised immediately without retry.
    '''

    # Arrange: fail with auth error.
    class AuthenticationError(Exception):
        pass

    fn = mock.Mock(side_effect=AuthenticationError('unauthorized'))

    # Execute and expect immediate error.
    with pytest.raises(TiferetError) as exc_info:
        RetryHandler.execute_with_retry(fn, max_retries=3, base_delay=0.01)

    # Assert only one attempt was made.
    assert fn.call_count == 1
    assert exc_info.value.error_code == const.LLM_AUTH_ERROR_ID


# ** test: classify_rate_limit_error
def test_classify_rate_limit_error():
    '''
    Test classification of rate limit errors.
    '''

    # Create a rate limit error.
    class RateLimitError(Exception):
        pass

    result = RetryHandler._classify_error(RateLimitError('rate limited'))
    assert result == const.LLM_RATE_LIMIT_ERROR_ID


# ** test: classify_context_length_error
def test_classify_context_length_error():
    '''
    Test classification of context length errors.
    '''

    error = Exception('context_length exceeded for this model')
    result = RetryHandler._classify_error(error)
    assert result == const.LLM_CONTEXT_LENGTH_ERROR_ID


# ** test: classify_timeout_error
def test_classify_timeout_error():
    '''
    Test classification of timeout errors.
    '''

    result = RetryHandler._classify_error(TimeoutError('connection timed out'))
    assert result == const.LLM_TIMEOUT_ERROR_ID


# ** test: classify_quota_exceeded_error
def test_classify_quota_exceeded_error():
    '''
    Test classification of quota exhaustion errors.
    '''

    # Test insufficient_quota pattern.
    error = Exception('Error code: 429 - insufficient_quota')
    result = RetryHandler._classify_error(error)
    assert result == const.LLM_QUOTA_EXCEEDED_ID

    # Test exceeded your current quota pattern.
    error = Exception('You exceeded your current quota, please check your plan.')
    result = RetryHandler._classify_error(error)
    assert result == const.LLM_QUOTA_EXCEEDED_ID


# ** test: retry_handler_non_retryable_quota_error
def test_retry_handler_non_retryable_quota_error():
    '''
    Test that quota exhaustion errors are raised immediately without retry.
    '''

    # Arrange: fail with quota error.
    fn = mock.Mock(side_effect=Exception('insufficient_quota'))

    # Execute and expect immediate error.
    with pytest.raises(TiferetError) as exc_info:
        RetryHandler.execute_with_retry(fn, max_retries=3, base_delay=0.01)

    # Assert only one attempt was made.
    assert fn.call_count == 1
    assert exc_info.value.error_code == const.LLM_QUOTA_EXCEEDED_ID


# ** test: classify_generic_error
def test_classify_generic_error():
    '''
    Test that unrecognized errors classify as generic invocation errors.
    '''

    error = Exception('something unexpected happened')
    result = RetryHandler._classify_error(error)
    assert result == const.LLM_INVOCATION_ERROR_ID
