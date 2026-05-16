"""
Multi-Tool Agent Example — tiferet-agents

Demonstrates an agent with multiple registered tools, showing
how to configure tools via AgentToolAggregate and use them in
a SendMessage flow.

Prerequisites:
    pip install tiferet-agents
    export OPENAI_API_KEY=<your-key>

Usage:
    python examples/multi_tool_agent.py
"""

from unittest import mock

from langchain_core.tools import tool
from tiferet.events import DomainEvent

from tiferet_agents import SendMessage
from tiferet_agents.interfaces import (
    AgentService, ConversationService,
)
from tiferet_agents.mappers.agent import (
    AgentConfigurationAggregate, AgentToolAggregate,
)
from tiferet_agents.utils.providers import LLMProviderFactory


# Define some example tools as LangChain @tool functions.
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # Simulated weather data.
    weather_data = {
        'new york': 'Sunny, 72°F',
        'london': 'Cloudy, 58°F',
        'tokyo': 'Rainy, 65°F',
    }
    return weather_data.get(city.lower(), f'Weather data not available for {city}')


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)  # noqa: S307
        return str(result)
    except Exception as e:
        return f'Error: {e}'


def main():
    """Run the multi-tool agent example."""

    # Create an agent with tools configured.
    agent = AgentConfigurationAggregate(
        id='multi-tool-agent',
        name='Multi-Tool Agent',
        provider='openai',
        model='gpt-4o-mini',
        system_prompt=(
            'You are a helpful assistant with access to weather and calculator tools. '
            'Use them when appropriate to answer questions.'
        ),
        temperature=0.7,
    )

    # Register tools on the agent.
    agent.add_tool(AgentToolAggregate(
        id='weather',
        name='Weather',
        description='Get current weather for a city',
        module_path='examples.multi_tool_agent',
        class_name='get_weather',
    ))
    agent.add_tool(AgentToolAggregate(
        id='calculator',
        name='Calculator',
        description='Evaluate mathematical expressions',
        module_path='examples.multi_tool_agent',
        class_name='calculate',
    ))

    # Set up services.
    agent_service = mock.Mock(spec=AgentService)
    agent_service.get.return_value = agent

    conversation_service = mock.Mock(spec=ConversationService)
    conversation_service.get.return_value = None

    llm_service = LLMProviderFactory()

    # Test queries that use different tools.
    queries = [
        "What's the weather in Tokyo?",
        "What is 42 * 17 + 3?",
        "How's the weather in London?",
    ]

    for query in queries:
        print(f"User: {query}")
        result = DomainEvent.handle(
            SendMessage,
            dependencies={
                'agent_service': agent_service,
                'conversation_service': conversation_service,
                'llm_provider_service': llm_service,
            },
            agent_id='multi-tool-agent',
            message=query,
        )
        print(f"Agent: {result.content}\n")


if __name__ == '__main__':
    main()
