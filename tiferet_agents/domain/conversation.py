"""tiferet_agents Conversation Domain"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import Any, List, Optional
from uuid import uuid4

# ** infra
from pydantic import Field, model_validator

# ** app
from tiferet.domain import DomainObject

# *** models

# ** model: message
class Message(DomainObject):
    '''
    A single message within a conversation.

    Messages represent turns in an agent conversation, including
    human inputs, AI responses, system prompts, and tool outputs.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='UUID string uniquely identifying this message.',
    )

    # * attribute: conversation_id
    conversation_id: str = Field(
        ...,
        description='UUID of the parent conversation.',
    )

    # * attribute: role
    role: str = Field(
        ...,
        description='Message role: system, human, ai, or tool.',
    )

    # * attribute: content
    content: str = Field(
        default='',
        description='Text content of the message.',
    )

    # * attribute: tool_calls
    tool_calls: List[dict] = Field(
        default_factory=list,
        description='Tool call requests from the AI (for ai role messages).',
    )

    # * attribute: tool_call_id
    tool_call_id: Optional[str] = Field(
        default=None,
        description='ID of the tool call this message responds to (for tool role).',
    )

    # * attribute: created_at
    created_at: str = Field(
        ...,
        description='ISO 8601 creation timestamp.',
    )

    # * method: _derive_defaults (validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_defaults(cls, data: Any) -> Any:
        '''
        Derive default values for id and created_at when absent.

        :param data: The raw input data.
        :type data: Any
        :return: The augmented input data.
        :rtype: Any
        '''

        # Only mutate dict-shaped inputs.
        if not isinstance(data, dict):
            return data
        data = dict(data)

        # Generate a UUID if id is not provided.
        if not data.get('id'):
            data['id'] = str(uuid4())

        # Set timestamp if not provided.
        if not data.get('created_at'):
            data['created_at'] = datetime.now(timezone.utc).isoformat()

        # Return the augmented data.
        return data


# ** model: conversation
class Conversation(DomainObject):
    '''
    An agent conversation session.

    A conversation tracks a thread of messages between a user and an
    agent, identified by a thread_id for LangGraph checkpointer integration.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='UUID string uniquely identifying this conversation.',
    )

    # * attribute: agent_id
    agent_id: str = Field(
        ...,
        description='ID of the agent configuration used in this conversation.',
    )

    # * attribute: thread_id
    thread_id: str = Field(
        ...,
        description='LangGraph thread identifier for checkpointer state.',
    )

    # * attribute: title
    title: str = Field(
        default='',
        description='Optional human-readable conversation title.',
    )

    # * attribute: status
    status: str = Field(
        default='active',
        description='Conversation status: active or archived.',
    )

    # * attribute: created_at
    created_at: str = Field(
        ...,
        description='ISO 8601 creation timestamp.',
    )

    # * attribute: updated_at
    updated_at: str = Field(
        ...,
        description='ISO 8601 last-updated timestamp.',
    )

    # * attribute: messages
    messages: List[Message] = Field(
        default_factory=list,
        description='Ordered list of messages in this conversation.',
    )

    # * method: _derive_defaults (validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_defaults(cls, data: Any) -> Any:
        '''
        Derive default values for id, thread_id, created_at, and updated_at.

        :param data: The raw input data.
        :type data: Any
        :return: The augmented input data.
        :rtype: Any
        '''

        # Only mutate dict-shaped inputs.
        if not isinstance(data, dict):
            return data
        data = dict(data)

        # Generate UUIDs if not provided.
        if not data.get('id'):
            data['id'] = str(uuid4())
        if not data.get('thread_id'):
            data['thread_id'] = str(uuid4())

        # Set timestamps if not provided.
        now = datetime.now(timezone.utc).isoformat()
        if not data.get('created_at'):
            data['created_at'] = now
        if not data.get('updated_at'):
            data['updated_at'] = now

        # Return the augmented data.
        return data

    # * method: message_count
    def message_count(self) -> int:
        '''
        Return the number of messages in this conversation.

        :return: The message count.
        :rtype: int
        '''

        # Return the length of the messages list.
        return len(self.messages)
