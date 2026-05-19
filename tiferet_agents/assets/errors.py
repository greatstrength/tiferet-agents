"""tiferet_agents Default Errors (Assets)"""

# *** imports

# ** app
from . import constants as const

# *** constants

# ** constant: default_errors
DEFAULT_ERRORS = {

    # * error: AGENT_NOT_FOUND
    const.AGENT_NOT_FOUND_ID: {
        'id': const.AGENT_NOT_FOUND_ID,
        'name': 'Agent Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Agent not found: {agent_id}.'}
        ]
    },

    # * error: AGENT_ALREADY_EXISTS
    const.AGENT_ALREADY_EXISTS_ID: {
        'id': const.AGENT_ALREADY_EXISTS_ID,
        'name': 'Agent Already Exists',
        'message': [
            {'lang': 'en_US', 'text': 'Agent already exists: {agent_id}.'}
        ]
    },

    # * error: INVALID_AGENT_ATTRIBUTE
    const.INVALID_AGENT_ATTRIBUTE_ID: {
        'id': const.INVALID_AGENT_ATTRIBUTE_ID,
        'name': 'Invalid Agent Attribute',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid agent attribute: {attribute}.'}
        ]
    },

    # * error: INVALID_PROVIDER
    const.INVALID_PROVIDER_ID: {
        'id': const.INVALID_PROVIDER_ID,
        'name': 'Invalid Provider',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid or unsupported LLM provider: {provider}.'}
        ]
    },

    # * error: CONVERSATION_NOT_FOUND
    const.CONVERSATION_NOT_FOUND_ID: {
        'id': const.CONVERSATION_NOT_FOUND_ID,
        'name': 'Conversation Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Conversation not found: {conversation_id}.'}
        ]
    },

    # * error: CONVERSATION_ALREADY_EXISTS
    const.CONVERSATION_ALREADY_EXISTS_ID: {
        'id': const.CONVERSATION_ALREADY_EXISTS_ID,
        'name': 'Conversation Already Exists',
        'message': [
            {'lang': 'en_US', 'text': 'Conversation already exists: {conversation_id}.'}
        ]
    },

    # * error: INVALID_CONVERSATION_STATUS
    const.INVALID_CONVERSATION_STATUS_ID: {
        'id': const.INVALID_CONVERSATION_STATUS_ID,
        'name': 'Invalid Conversation Status',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid conversation status: {status}.'}
        ]
    },

    # * error: INVALID_MESSAGE_ROLE
    const.INVALID_MESSAGE_ROLE_ID: {
        'id': const.INVALID_MESSAGE_ROLE_ID,
        'name': 'Invalid Message Role',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid message role: {role}.'}
        ]
    },

    # * error: GRAPH_BUILD_ERROR
    const.GRAPH_BUILD_ERROR_ID: {
        'id': const.GRAPH_BUILD_ERROR_ID,
        'name': 'Graph Build Error',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to build agent graph for {agent_id}: {error}.'}
        ]
    },

    # * error: LLM_INVOCATION_ERROR
    const.LLM_INVOCATION_ERROR_ID: {
        'id': const.LLM_INVOCATION_ERROR_ID,
        'name': 'LLM Invocation Error',
        'message': [
            {'lang': 'en_US', 'text': 'LLM invocation failed: {error}.'}
        ]
    },

    # * error: TOOL_NOT_FOUND
    const.TOOL_NOT_FOUND_ID: {
        'id': const.TOOL_NOT_FOUND_ID,
        'name': 'Tool Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Tool not found: {tool_id}.'}
        ]
    },

    # * error: TOOL_LOAD_ERROR
    const.TOOL_LOAD_ERROR_ID: {
        'id': const.TOOL_LOAD_ERROR_ID,
        'name': 'Tool Load Error',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to load tool {tool_id}: {error}.'}
        ]
    },

    # * error: INVALID_GRAPH_TYPE
    const.INVALID_GRAPH_TYPE_ID: {
        'id': const.INVALID_GRAPH_TYPE_ID,
        'name': 'Invalid Graph Type',
        'message': [
            {'lang': 'en_US', 'text': 'Unsupported graph type: {graph_type} for agent {agent_id}.'}
        ]
    },

    # * error: EMBEDDING_ERROR
    const.EMBEDDING_ERROR_ID: {
        'id': const.EMBEDDING_ERROR_ID,
        'name': 'Embedding Error',
        'message': [
            {'lang': 'en_US', 'text': 'Embedding generation failed: {error}.'}
        ]
    },

    # * error: MEMORY_NAMESPACE_NOT_FOUND
    const.MEMORY_NAMESPACE_NOT_FOUND_ID: {
        'id': const.MEMORY_NAMESPACE_NOT_FOUND_ID,
        'name': 'Memory Namespace Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Memory namespace not found: {namespace_id}.'}
        ]
    },

    # * error: MEMORY_FACT_NOT_FOUND
    const.MEMORY_FACT_NOT_FOUND_ID: {
        'id': const.MEMORY_FACT_NOT_FOUND_ID,
        'name': 'Memory Fact Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Memory fact not found: {fact_id}.'}
        ]
    },

    # * error: LLM_RATE_LIMIT_ERROR
    const.LLM_RATE_LIMIT_ERROR_ID: {
        'id': const.LLM_RATE_LIMIT_ERROR_ID,
        'name': 'LLM Rate Limit Error',
        'message': [
            {'lang': 'en_US', 'text': 'LLM rate limit exceeded, please retry later: {error}.'}
        ]
    },

    # * error: LLM_CONTEXT_LENGTH_ERROR
    const.LLM_CONTEXT_LENGTH_ERROR_ID: {
        'id': const.LLM_CONTEXT_LENGTH_ERROR_ID,
        'name': 'LLM Context Length Error',
        'message': [
            {'lang': 'en_US', 'text': 'LLM context length exceeded: {error}.'}
        ]
    },

    # * error: LLM_AUTH_ERROR
    const.LLM_AUTH_ERROR_ID: {
        'id': const.LLM_AUTH_ERROR_ID,
        'name': 'LLM Authentication Error',
        'message': [
            {'lang': 'en_US', 'text': 'LLM authentication failed: {error}.'}
        ]
    },

    # * error: LLM_TIMEOUT_ERROR
    const.LLM_TIMEOUT_ERROR_ID: {
        'id': const.LLM_TIMEOUT_ERROR_ID,
        'name': 'LLM Timeout Error',
        'message': [
            {'lang': 'en_US', 'text': 'LLM request timed out: {error}.'}
        ]
    },

    # * error: LLM_QUOTA_EXCEEDED
    const.LLM_QUOTA_EXCEEDED_ID: {
        'id': const.LLM_QUOTA_EXCEEDED_ID,
        'name': 'LLM Quota Exceeded',
        'message': [
            {'lang': 'en_US', 'text': 'LLM quota exceeded, check your billing plan: {error}.'}
        ]
    },

    # * error: TOOL_APPROVAL_REQUIRED
    const.TOOL_APPROVAL_REQUIRED_ID: {
        'id': const.TOOL_APPROVAL_REQUIRED_ID,
        'name': 'Tool Approval Required',
        'message': [
            {'lang': 'en_US', 'text': 'Tool call requires human approval: {tool_call_id}.'}
        ]
    },

    # * error: TOOL_CALL_NOT_FOUND
    const.TOOL_CALL_NOT_FOUND_ID: {
        'id': const.TOOL_CALL_NOT_FOUND_ID,
        'name': 'Tool Call Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Pending tool call not found: {tool_call_id}.'}
        ]
    },

    # * error: INVALID_CHECKPOINTER_TYPE
    const.INVALID_CHECKPOINTER_TYPE_ID: {
        'id': const.INVALID_CHECKPOINTER_TYPE_ID,
        'name': 'Invalid Checkpointer Type',
        'message': [
            {'lang': 'en_US', 'text': 'Unsupported checkpointer type: {checkpointer_type}.'}
        ]
    },
}
