"""tiferet_agents Interfaces Conversation"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List, Optional

# ** app
from tiferet.interfaces import Service

# *** interfaces

# ** interface: conversation_service
class ConversationService(Service):
    '''
    Service interface for managing agent conversations and messages.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if a conversation exists by ID.

        :param id: The conversation identifier.
        :type id: str
        :return: True if the conversation exists, otherwise False.
        :rtype: bool
        '''
        raise NotImplementedError()

    # * method: get
    @abstractmethod
    def get(self, id: str):
        '''
        Retrieve a conversation by ID, including its messages.

        :param id: The conversation identifier.
        :type id: str
        :return: The conversation aggregate with messages, or None.
        '''
        raise NotImplementedError()

    # * method: list
    @abstractmethod
    def list(self, agent_id: Optional[str] = None, status: Optional[str] = None) -> List:
        '''
        List conversations with optional filters.

        :param agent_id: Optional agent identifier to filter by.
        :type agent_id: str | None
        :param status: Optional status to filter by.
        :type status: str | None
        :return: A list of conversation aggregates.
        :rtype: List
        '''
        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, conversation) -> None:
        '''
        Save or update a conversation.

        :param conversation: The conversation aggregate to save.
        :return: None
        :rtype: None
        '''
        raise NotImplementedError()

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete a conversation by ID.

        :param id: The conversation identifier.
        :type id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError()

    # * method: add_message
    @abstractmethod
    def add_message(self, conversation_id: str, message) -> None:
        '''
        Add a message to a conversation.

        :param conversation_id: The conversation identifier.
        :type conversation_id: str
        :param message: The message aggregate to add.
        :return: None
        :rtype: None
        '''
        raise NotImplementedError()

    # * method: get_messages
    @abstractmethod
    def get_messages(self, conversation_id: str) -> List:
        '''
        Retrieve all messages for a conversation.

        :param conversation_id: The conversation identifier.
        :type conversation_id: str
        :return: A list of message aggregates.
        :rtype: List
        '''
        raise NotImplementedError()
