"""tiferet_agents Conversation Mappers"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import List

# ** infra
from pydantic import Field

# ** app
from tiferet.mappers import Aggregate

from ..domain.conversation import Conversation, Message

# *** mappers

# ** mapper: message_aggregate
class MessageAggregate(Message, Aggregate):
    '''
    A mutable aggregate representation of a message.
    '''
    pass


# ** mapper: conversation_aggregate
class ConversationAggregate(Conversation, Aggregate):
    '''
    A mutable aggregate representation of a conversation.
    '''

    # * attribute: messages
    messages: List[MessageAggregate] = Field(
        default_factory=list,
        description='Mutable list of message aggregates.',
    )

    # * method: rename
    def rename(self, title: str) -> None:
        '''
        Rename the conversation.

        :param title: The new conversation title.
        :type title: str
        '''

        # Update the title and timestamp.
        self.title = title
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: set_status
    def set_status(self, status: str) -> None:
        '''
        Set the conversation status.

        :param status: The new status (active, archived).
        :type status: str
        '''

        # Update the status and timestamp.
        self.status = status
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # * method: add_message
    def add_message(self, message: MessageAggregate) -> None:
        '''
        Add a message to the conversation.

        :param message: The message to add.
        :type message: MessageAggregate
        '''

        # Append the message and update the timestamp.
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc).isoformat()
