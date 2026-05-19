"""tiferet_agents In-Memory Conversation Repository"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import Dict, List, Optional

# ** app
from tiferet.events import RaiseError

from ..assets import constants as const
from ..interfaces.conversation import ConversationService
from ..mappers.conversation import ConversationAggregate, MessageAggregate

# *** repos

# ** repo: in_memory_conversation_repository
class InMemoryConversationRepository(ConversationService):
    '''
    In-memory ConversationService implementation backed by a plain dict store.

    Designed for prototyping, testing, and lightweight use cases where
    persistent storage is not required. All data is lost when the
    process ends.
    '''

    # * attribute: _store
    _store: Dict[str, ConversationAggregate]

    # * init
    def __init__(self):
        '''
        Initialize the in-memory conversation store.
        '''

        # Initialize the empty store.
        self._store = {}

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if a conversation exists by ID.

        :param id: The conversation identifier.
        :type id: str
        :return: True if the conversation exists.
        :rtype: bool
        '''

        # Check the store.
        return id in self._store

    # * method: get
    def get(self, id: str) -> Optional[ConversationAggregate]:
        '''
        Retrieve a conversation by ID, including its messages.

        :param id: The conversation identifier.
        :type id: str
        :return: The conversation aggregate, or None.
        :rtype: ConversationAggregate | None
        '''

        # Return the conversation or None.
        return self._store.get(id)

    # * method: list
    def list(self, agent_id: Optional[str] = None, status: Optional[str] = None) -> List[ConversationAggregate]:
        '''
        List conversations with optional filters.

        :param agent_id: Optional agent identifier to filter by.
        :type agent_id: str | None
        :param status: Optional status to filter by.
        :type status: str | None
        :return: A list of conversation aggregates.
        :rtype: List[ConversationAggregate]
        '''

        # Start with all conversations.
        results = list(self._store.values())

        # Filter by agent_id if provided.
        if agent_id is not None:
            results = [c for c in results if c.agent_id == agent_id]

        # Filter by status if provided.
        if status is not None:
            results = [c for c in results if c.status == status]

        # Return filtered results.
        return results

    # * method: save
    def save(self, conversation: ConversationAggregate) -> None:
        '''
        Save or update a conversation.

        :param conversation: The conversation aggregate to save.
        :type conversation: ConversationAggregate
        '''

        # Store by ID.
        self._store[conversation.id] = conversation

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete a conversation by ID. Idempotent.

        :param id: The conversation identifier.
        :type id: str
        '''

        # Remove if present.
        self._store.pop(id, None)

    # * method: add_message
    def add_message(self, conversation_id: str, message: MessageAggregate) -> None:
        '''
        Add a message to a conversation.

        :param conversation_id: The conversation identifier.
        :type conversation_id: str
        :param message: The message aggregate to add.
        :type message: MessageAggregate
        '''

        # Retrieve the conversation.
        conversation = self._store.get(conversation_id)

        # Verify the conversation exists.
        if conversation is None:
            RaiseError.execute(
                error_code=const.CONVERSATION_NOT_FOUND_ID,
                conversation_id=conversation_id,
            )

        # Add the message via aggregate method.
        conversation.add_message(message)

    # * method: get_messages
    def get_messages(self, conversation_id: str) -> List[MessageAggregate]:
        '''
        Retrieve all messages for a conversation.

        :param conversation_id: The conversation identifier.
        :type conversation_id: str
        :return: A list of message aggregates.
        :rtype: List[MessageAggregate]
        '''

        # Retrieve the conversation.
        conversation = self._store.get(conversation_id)

        # Return empty list if conversation not found.
        if conversation is None:
            return []

        # Return the messages.
        return conversation.messages
