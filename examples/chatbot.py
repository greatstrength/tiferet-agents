"""
Basic Chatbot Example — tiferet-agents

Demonstrates a simple conversational agent using YAML configuration
and the SendMessage event via DomainEvent.handle().

Prerequisites:
    pip install tiferet-agents
    export OPENAI_API_KEY=<your-key>

Usage:
    python examples/chatbot.py
"""

from unittest import mock

from tiferet.events import DomainEvent

from tiferet_agents import SendMessage
from tiferet_agents.interfaces import (
    AgentService, ConversationService, LLMProviderService,
)
from tiferet_agents.mappers.agent import AgentConfigurationAggregate
from tiferet_agents.mappers.conversation import ConversationAggregate, MessageAggregate
from tiferet_agents.utils.providers import LLMProviderFactory


def main():
    """Run the chatbot example."""

    # Create a simple agent configuration.
    agent = AgentConfigurationAggregate(
        id='chatbot',
        name='Chatbot',
        provider='openai',
        model='gpt-4o-mini',
        system_prompt='You are a friendly chatbot. Be concise.',
        temperature=0.7,
    )

    # Set up mock services for the example.
    agent_service = mock.Mock(spec=AgentService)
    agent_service.get.return_value = agent

    conversation_service = mock.Mock(spec=ConversationService)
    conversation_service.get.return_value = None

    llm_service = LLMProviderFactory()

    # Simple conversation loop.
    print("Chatbot ready! Type 'quit' to exit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ('quit', 'exit'):
            break

        result = DomainEvent.handle(
            SendMessage,
            dependencies={
                'agent_service': agent_service,
                'conversation_service': conversation_service,
                'llm_provider_service': llm_service,
            },
            agent_id='chatbot',
            message=user_input,
        )

        print(f"Bot: {result.content}\n")


if __name__ == '__main__':
    main()
