"""tiferet_agents Approval Events"""

# *** imports

# ** core
from typing import Any

# ** app
from tiferet.events import DomainEvent

from ..assets import constants as const
from ..interfaces.agent import AgentService
from ..interfaces.llm import LLMProviderService
from ..utils.graph import GraphBuilder

# *** events

# ** event: approve_tool_call
class ApproveToolCall(DomainEvent):
    '''
    Event to approve a pending tool call on a paused agent graph.

    Resumes graph execution from the interrupt point, allowing the
    pending tool call to proceed.
    '''

    # * attribute: agent_service
    agent_service: AgentService

    # * attribute: llm_provider_service
    llm_provider_service: LLMProviderService

    # * init
    def __init__(self,
            agent_service: AgentService,
            llm_provider_service: LLMProviderService,
        ):
        '''
        Initialize the ApproveToolCall event.

        :param agent_service: The agent service for loading configurations.
        :type agent_service: AgentService
        :param llm_provider_service: The LLM provider service.
        :type llm_provider_service: LLMProviderService
        '''

        # Set dependencies.
        self.agent_service = agent_service
        self.llm_provider_service = llm_provider_service

    # * method: execute
    @DomainEvent.parameters_required(['agent_id', 'thread_id', 'graph'])
    def execute(self,
            agent_id: str,
            thread_id: str,
            graph: Any,
            **kwargs,
        ) -> dict:
        '''
        Approve and resume a pending tool call.

        :param agent_id: The agent configuration identifier.
        :type agent_id: str
        :param thread_id: The thread ID of the paused graph.
        :type thread_id: str
        :param graph: The compiled LangGraph graph instance.
        :type graph: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The graph output state dict after resumption.
        :rtype: dict
        '''

        # Verify the agent exists.
        agent = self.agent_service.get(agent_id)
        self.verify(
            expression=agent is not None,
            error_code=const.AGENT_NOT_FOUND_ID,
            agent_id=agent_id,
        )

        # Resume the graph with approval.
        result = GraphBuilder.resume(
            graph=graph,
            thread_id=thread_id,
            approve=True,
        )

        # Return the result.
        return result


# ** event: deny_tool_call
class DenyToolCall(DomainEvent):
    '''
    Event to deny a pending tool call on a paused agent graph.

    Rejects the pending tool call and continues graph execution
    with a denial message.
    '''

    # * attribute: agent_service
    agent_service: AgentService

    # * attribute: llm_provider_service
    llm_provider_service: LLMProviderService

    # * init
    def __init__(self,
            agent_service: AgentService,
            llm_provider_service: LLMProviderService,
        ):
        '''
        Initialize the DenyToolCall event.

        :param agent_service: The agent service for loading configurations.
        :type agent_service: AgentService
        :param llm_provider_service: The LLM provider service.
        :type llm_provider_service: LLMProviderService
        '''

        # Set dependencies.
        self.agent_service = agent_service
        self.llm_provider_service = llm_provider_service

    # * method: execute
    @DomainEvent.parameters_required(['agent_id', 'thread_id', 'graph'])
    def execute(self,
            agent_id: str,
            thread_id: str,
            graph: Any,
            **kwargs,
        ) -> dict:
        '''
        Deny and reject a pending tool call.

        :param agent_id: The agent configuration identifier.
        :type agent_id: str
        :param thread_id: The thread ID of the paused graph.
        :type thread_id: str
        :param graph: The compiled LangGraph graph instance.
        :type graph: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The graph output state dict after denial.
        :rtype: dict
        '''

        # Verify the agent exists.
        agent = self.agent_service.get(agent_id)
        self.verify(
            expression=agent is not None,
            error_code=const.AGENT_NOT_FOUND_ID,
            agent_id=agent_id,
        )

        # Resume the graph with denial.
        result = GraphBuilder.resume(
            graph=graph,
            thread_id=thread_id,
            approve=False,
        )

        # Return the result.
        return result
