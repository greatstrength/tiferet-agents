"""tiferet_agents Conversation Events"""

# *** imports

# ** core
from typing import List

# ** app
from tiferet.events import DomainEvent

from ..assets import constants as const
from ..domain.conversation import Conversation, Message
from ..interfaces.agent import AgentService
from ..interfaces.conversation import ConversationService
from ..interfaces.llm import LLMProviderService
from ..mappers.conversation import ConversationAggregate, MessageAggregate
from ..utils.graph import GraphBuilder

# *** events

# ** event: send_message
class SendMessage(DomainEvent):
    '''
    Core event: send a user message to an agent and receive an AI response.

    Orchestrates the full flow: load agent config → build LLM → build graph
    → invoke → extract response → persist conversation → return message.
    '''

    # * attribute: agent_service
    agent_service: AgentService

    # * attribute: conversation_service
    conversation_service: ConversationService

    # * attribute: llm_provider_service
    llm_provider_service: LLMProviderService

    # * init
    def __init__(self,
            agent_service: AgentService,
            conversation_service: ConversationService,
            llm_provider_service: LLMProviderService,
        ):
        '''
        Initialize the SendMessage event.

        :param agent_service: Service for loading agent configurations.
        :type agent_service: AgentService
        :param conversation_service: Service for conversation persistence.
        :type conversation_service: ConversationService
        :param llm_provider_service: Service for creating LLM instances.
        :type llm_provider_service: LLMProviderService
        '''

        # Set dependencies.
        self.agent_service = agent_service
        self.conversation_service = conversation_service
        self.llm_provider_service = llm_provider_service

    # * method: execute
    @DomainEvent.parameters_required(['agent_id', 'message'])
    def execute(self,
            agent_id: str,
            message: str,
            conversation_id: str | None = None,
            **kwargs,
        ) -> Message:
        '''
        Send a message to an agent and return the AI response.

        :param agent_id: The agent configuration identifier.
        :type agent_id: str
        :param message: The user message content.
        :type message: str
        :param conversation_id: Optional existing conversation ID.
        :type conversation_id: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The AI response message.
        :rtype: Message
        '''

        # Load the agent configuration.
        agent = self.agent_service.get(agent_id)
        self.verify(
            expression=agent is not None,
            error_code=const.AGENT_NOT_FOUND_ID,
            agent_id=agent_id,
        )

        # Create the LLM model from agent config.
        chat_model = self.llm_provider_service.create_model(
            provider=agent.provider,
            model=agent.model,
            temperature=agent.temperature,
            max_tokens=agent.max_tokens,
        )

        # Get or create the conversation.
        conversation = None
        if conversation_id:
            conversation = self.conversation_service.get(conversation_id)

        if conversation is None:
            conversation = ConversationAggregate(agent_id=agent_id)

        # Build the graph (no tools for alpha — tool loading comes in a2).
        graph = GraphBuilder.build(
            agent_config=agent,
            chat_model=chat_model,
        )

        # Invoke the graph.
        result = GraphBuilder.invoke(
            graph=graph,
            message=message,
        )

        # Extract the AI response from the result.
        ai_content = ''
        if result and 'messages' in result:
            messages = result['messages']
            if messages:
                last_msg = messages[-1]
                ai_content = getattr(last_msg, 'content', str(last_msg))

        # Create the user message aggregate.
        user_msg = MessageAggregate(
            conversation_id=conversation.id,
            role='human',
            content=message,
        )

        # Create the AI response message aggregate.
        ai_msg = MessageAggregate(
            conversation_id=conversation.id,
            role='ai',
            content=ai_content,
        )

        # Add messages to the conversation.
        conversation.add_message(user_msg)
        conversation.add_message(ai_msg)

        # Persist the conversation.
        self.conversation_service.save(conversation)

        # Return the AI response message.
        return ai_msg


# ** event: get_conversation
class GetConversation(DomainEvent):
    '''
    Event to retrieve a conversation by ID.
    '''

    # * attribute: conversation_service
    conversation_service: ConversationService

    # * init
    def __init__(self, conversation_service: ConversationService):
        '''
        Initialize the GetConversation event.

        :param conversation_service: The conversation service.
        :type conversation_service: ConversationService
        '''

        # Set the conversation service dependency.
        self.conversation_service = conversation_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> Conversation:
        '''
        Retrieve a conversation by ID.

        :param id: The conversation identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The conversation with messages.
        :rtype: Conversation
        '''

        # Retrieve the conversation.
        conversation = self.conversation_service.get(id)

        # Verify it exists.
        self.verify(
            expression=conversation is not None,
            error_code=const.CONVERSATION_NOT_FOUND_ID,
            conversation_id=id,
        )

        # Return the conversation.
        return conversation


# ** event: list_conversations
class ListConversations(DomainEvent):
    '''
    Event to list conversations with optional filters.
    '''

    # * attribute: conversation_service
    conversation_service: ConversationService

    # * init
    def __init__(self, conversation_service: ConversationService):
        '''
        Initialize the ListConversations event.

        :param conversation_service: The conversation service.
        :type conversation_service: ConversationService
        '''

        # Set the conversation service dependency.
        self.conversation_service = conversation_service

    # * method: execute
    def execute(self,
            agent_id: str | None = None,
            status: str | None = None,
            **kwargs,
        ) -> List[Conversation]:
        '''
        List conversations with optional filters.

        :param agent_id: Optional agent ID filter.
        :type agent_id: str | None
        :param status: Optional status filter.
        :type status: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A list of conversations.
        :rtype: List[Conversation]
        '''

        # Return filtered conversations.
        return self.conversation_service.list(agent_id=agent_id, status=status)
