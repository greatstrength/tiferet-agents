"""tiferet_agents Utils Graph"""

# *** imports

# ** core
import importlib
from typing import Any, Generator, List, Optional, Sequence

# ** infra
from langgraph.prebuilt import create_react_agent

# ** app
from tiferet.events import RaiseError

from ..assets import constants as const
from ..mappers.agent import AgentConfigurationAggregate
from .retry import RetryHandler

# *** utils

# ** util: graph_builder
class GraphBuilder:
    '''
    Utility for building LangGraph agent graphs from AgentConfigurationAggregate objects.

    Wraps LangGraph's ``create_react_agent`` to produce a compiled graph
    ready for ``.invoke()`` or ``.stream()`` calls.
    '''

    # * method: build (static)
    @staticmethod
    def build(
            agent_config: AgentConfigurationAggregate,
            chat_model: Any,
            tools: Sequence = (),
            checkpointer: Any = None,
            store: Any = None,
        ) -> Any:
        '''
        Build a compiled LangGraph agent from configuration.

        Dispatches to the appropriate builder based on agent_config.graph_type.
        If any tool has requires_approval=True and a checkpointer is provided,
        interrupt_before is configured for those tools.

        :param agent_config: The agent configuration.
        :type agent_config: AgentConfigurationAggregate
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

        # Resolve graph type from agent configuration.
        graph_type = getattr(agent_config, 'graph_type', 'react')

        # Dispatch to the appropriate builder.
        if graph_type == 'react':
            return GraphBuilder._build_react(
                agent_config=agent_config,
                chat_model=chat_model,
                tools=tools,
                checkpointer=checkpointer,
                store=store,
            )

        # Unsupported graph type.
        RaiseError.execute(
            error_code=const.INVALID_GRAPH_TYPE_ID,
            graph_type=graph_type,
            agent_id=agent_config.id,
        )

    # * method: _build_react (static)
    @staticmethod
    def _build_react(
            agent_config: AgentConfigurationAggregate,
            chat_model: Any,
            tools: Sequence = (),
            checkpointer: Any = None,
            store: Any = None,
        ) -> Any:
        '''
        Build a ReAct agent graph using LangGraph's prebuilt create_react_agent.

        When any configured tool has requires_approval=True and a checkpointer
        is provided, the graph is built with interrupt_before=['tools'] to
        pause execution before tool calls for human approval.

        :param agent_config: The agent configuration.
        :type agent_config: AgentConfigurationAggregate
        :param chat_model: A LangChain-compatible chat model.
        :type chat_model: Any
        :param tools: Sequence of LangChain tools.
        :type tools: Sequence
        :param checkpointer: Optional LangGraph checkpointer.
        :type checkpointer: Any
        :param store: Optional LangGraph store.
        :type store: Any
        :return: A compiled LangGraph graph.
        :rtype: Any
        '''

        try:

            # Check if any tool requires approval.
            needs_approval = any(
                getattr(t, 'requires_approval', False)
                for t in (agent_config.tools or [])
            )

            # Build keyword arguments for create_react_agent.
            build_kwargs = dict(
                model=chat_model,
                tools=list(tools),
                prompt=agent_config.system_prompt,
                checkpointer=checkpointer,
                store=store,
            )

            # Add interrupt_before if approval is needed and checkpointer is available.
            if needs_approval and checkpointer is not None:
                build_kwargs['interrupt_before'] = ['tools']

            # Build the graph using LangGraph's prebuilt ReAct agent.
            graph = create_react_agent(**build_kwargs)

            # Return the compiled graph.
            return graph

        except Exception as e:

            # Wrap any build failure as a structured error.
            RaiseError.execute(
                error_code=const.GRAPH_BUILD_ERROR_ID,
                agent_id=agent_config.id,
                error=str(e),
            )

    # * method: load_tools (static)
    @staticmethod
    def load_tools(agent_config: AgentConfigurationAggregate) -> List:
        '''
        Load and instantiate tools from an agent configuration.

        Iterates over agent_config.tools, imports each module_path.class_name,
        and resolves to either a constructor (class/function) or a pre-built
        tool object (e.g., @tool-decorated). Static parameters are applied
        in both cases.

        :param agent_config: The agent configuration with tool definitions.
        :type agent_config: AgentConfigurationAggregate
        :return: A list of instantiated tool callables.
        :rtype: List
        '''

        # Return empty list if no tools configured.
        if not agent_config.tools:
            return []

        loaded = []
        for tool_def in agent_config.tools:

            try:

                # Import the module and resolve the class/function.
                module = importlib.import_module(tool_def.module_path)
                tool_obj = getattr(module, tool_def.class_name)

                # Determine if the resolved object is a pre-built tool instance
                # (e.g., @tool-decorated) or a constructor that needs instantiation.
                if GraphBuilder._is_tool_instance(tool_obj):

                    # Pre-built tool: bind static parameters if provided.
                    tool_instance = GraphBuilder._bind_params_to_tool(
                        tool_obj, tool_def.parameters or {},
                    )

                elif isinstance(tool_obj, type) or callable(tool_obj):

                    # Constructor or factory: instantiate with static parameters.
                    if tool_def.parameters:
                        tool_instance = tool_obj(**tool_def.parameters)
                    else:
                        tool_instance = tool_obj()

                else:

                    # Unsupported tool shape.
                    RaiseError.execute(
                        error_code=const.TOOL_LOAD_ERROR_ID,
                        tool_id=tool_def.id,
                        error=f'Unsupported tool shape: {type(tool_obj).__name__}',
                    )

                loaded.append(tool_instance)

            except Exception as e:

                # Re-raise TiferetError without wrapping.
                from tiferet.assets.exceptions import TiferetError
                if isinstance(e, TiferetError):
                    raise

                # Wrap tool loading errors.
                RaiseError.execute(
                    error_code=const.TOOL_LOAD_ERROR_ID,
                    tool_id=tool_def.id,
                    error=str(e),
                )

        # Return the list of loaded tools.
        return loaded

    # * method: _is_tool_instance (static)
    @staticmethod
    def _is_tool_instance(obj: Any) -> bool:
        '''
        Check whether an object is an already-instantiated tool.

        Detects LangChain BaseTool instances and callable objects with
        tool-like attributes (name, description) that are not classes.

        :param obj: The resolved object from module import.
        :type obj: Any
        :return: True if the object is a pre-built tool instance.
        :rtype: bool
        '''

        # Check for LangChain BaseTool instances.
        try:
            from langchain_core.tools import BaseTool
            if isinstance(obj, BaseTool):
                return True
        except ImportError:
            pass

        # Check for callable objects with tool-like attributes that are not classes.
        if not isinstance(obj, type) and callable(obj) and hasattr(obj, 'name') and hasattr(obj, 'description'):
            return True

        # Not a pre-built tool.
        return False

    # * method: _bind_params_to_tool (static)
    @staticmethod
    def _bind_params_to_tool(tool_obj: Any, params: dict) -> Any:
        '''
        Bind static configuration parameters to a pre-built tool object.

        For pre-built tools, static parameters are stored as attributes
        on the tool object without altering its name, description, or
        invocation schema.

        :param tool_obj: The pre-built tool instance.
        :type tool_obj: Any
        :param params: Static parameters to bind.
        :type params: dict
        :return: The tool with parameters bound.
        :rtype: Any
        '''

        # If no parameters, return the tool as-is.
        if not params:
            return tool_obj

        # Bind each parameter as an attribute on the tool.
        # Use object.__setattr__ to bypass Pydantic validation on
        # StructuredTool and other Pydantic-based tool objects.
        for key, value in params.items():
            try:
                setattr(tool_obj, key, value)
            except (ValueError, AttributeError):
                object.__setattr__(tool_obj, key, value)

        # Return the tool with bound parameters.
        return tool_obj

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

            # Classify and raise the error with the appropriate code.
            error_code = RetryHandler._classify_error(e)
            RaiseError.execute(
                error_code=error_code,
                error=str(e),
            )

    # * method: stream (static)
    @staticmethod
    def stream(
            graph: Any,
            message: str,
            thread_id: Optional[str] = None,
            stream_mode: str = 'messages',
        ) -> Generator:
        '''
        Stream a compiled graph invocation, yielding token chunks.

        :param graph: The compiled LangGraph graph.
        :type graph: Any
        :param message: The user message content.
        :type message: str
        :param thread_id: Optional thread ID for checkpointer state.
        :type thread_id: str | None
        :param stream_mode: The LangGraph stream mode.
        :type stream_mode: str
        :return: A generator yielding (chunk, metadata) tuples.
        :rtype: Generator
        '''

        # Build the input.
        inputs = {'messages': [('user', message)]}

        # Build config with thread_id if provided.
        config = {}
        if thread_id:
            config = {'configurable': {'thread_id': thread_id}}

        try:

            # Stream the graph and yield chunks.
            yield from graph.stream(
                inputs,
                config=config if config else None,
                stream_mode=stream_mode,
            )

        except Exception as e:

            # Classify and raise the error with the appropriate code.
            error_code = RetryHandler._classify_error(e)
            RaiseError.execute(
                error_code=error_code,
                error=str(e),
            )

    # * method: resume (static)
    @staticmethod
    def resume(
            graph: Any,
            thread_id: str,
            approve: bool = True,
        ) -> dict:
        '''
        Resume a paused graph after human approval/denial.

        :param graph: The compiled LangGraph graph.
        :type graph: Any
        :param thread_id: The thread ID of the paused graph.
        :type thread_id: str
        :param approve: Whether to approve (True) or deny (False) the tool call.
        :type approve: bool
        :return: The graph output state dict, or None if denied.
        :rtype: dict
        '''

        config = {'configurable': {'thread_id': thread_id}}

        try:

            if approve:

                # Resume execution: invoke with None input continues from interrupt.
                return graph.invoke(None, config=config)

            else:

                # Deny: send a rejection message and continue.
                from langgraph.types import Command
                return graph.invoke(
                    Command(resume={'action': 'deny'}),
                    config=config,
                )

        except Exception as e:

            # Classify and raise the error with the appropriate code.
            error_code = RetryHandler._classify_error(e)
            RaiseError.execute(
                error_code=error_code,
                error=str(e),
            )
