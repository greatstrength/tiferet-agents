"""tiferet_agents Utils Graph"""

# *** imports

# ** core
from typing import Any, List, Optional, Sequence

# ** infra
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

# ** app
from tiferet.events import RaiseError

from ..assets import constants as const
from ..domain.agent import AgentConfiguration

# *** utils

# ** util: graph_builder
class GraphBuilder:
    '''
    Utility for building LangGraph agent graphs from AgentConfiguration objects.

    Wraps LangGraph's ``create_react_agent`` to produce a compiled graph
    ready for ``.invoke()`` or ``.stream()`` calls.
    '''

    # * method: build (static)
    @staticmethod
    def build(
            agent_config: AgentConfiguration,
            chat_model: Any,
            tools: Sequence = (),
            checkpointer: Any = None,
            store: Any = None,
        ) -> Any:
        '''
        Build a compiled LangGraph agent from configuration.

        :param agent_config: The agent configuration.
        :type agent_config: AgentConfiguration
        :param chat_model: A LangChain-compatible chat model.
        :type chat_model: Any
        :param tools: Sequence of LangChain tools.
        :type tools: Sequence
        :param checkpointer: Optional LangGraph checkpointer for state persistence.
        :type checkpointer: Any
        :param store: Optional LangGraph store for cross-thread memory.
        :type store: Any
        :return: A compiled LangGraph graph.
        :rtype: Any
        '''

        try:

            # Build the graph using LangGraph's prebuilt ReAct agent.
            graph = create_react_agent(
                model=chat_model,
                tools=list(tools),
                prompt=agent_config.system_prompt,
                checkpointer=checkpointer,
                store=store,
            )

            # Return the compiled graph.
            return graph

        except Exception as e:

            # Wrap any build failure as a structured error.
            RaiseError.execute(
                error_code=const.GRAPH_BUILD_ERROR_ID,
                agent_id=agent_config.id,
                error=str(e),
            )

    # * method: invoke (static)
    @staticmethod
    def invoke(
            graph: Any,
            message: str,
            thread_id: Optional[str] = None,
        ) -> dict:
        '''
        Invoke a compiled graph with a user message.

        :param graph: The compiled LangGraph graph.
        :type graph: Any
        :param message: The user message content.
        :type message: str
        :param thread_id: Optional thread ID for checkpointer state.
        :type thread_id: str | None
        :return: The graph output state dict.
        :rtype: dict
        '''

        # Build the input.
        inputs = {'messages': [('user', message)]}

        # Build config with thread_id if provided.
        config = {}
        if thread_id:
            config = {'configurable': {'thread_id': thread_id}}

        try:

            # Invoke the graph and return the result.
            return graph.invoke(inputs, config=config if config else None)

        except Exception as e:

            # Wrap invocation errors.
            RaiseError.execute(
                error_code=const.LLM_INVOCATION_ERROR_ID,
                error=str(e),
            )
