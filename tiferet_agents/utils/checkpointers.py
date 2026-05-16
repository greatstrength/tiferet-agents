"""tiferet_agents Utils Checkpointers"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from tiferet.events import RaiseError

from ..assets import constants as const

# *** constants

# ** constant: invalid_checkpointer_type_id
INVALID_CHECKPOINTER_TYPE_ID = 'INVALID_CHECKPOINTER_TYPE'

# *** utils

# ** util: checkpointer_factory
class CheckpointerFactory:
    '''
    Factory utility for creating LangGraph checkpointer instances.

    Supports memory (default), sqlite, and postgres checkpointers.
    SQLite and Postgres require optional extras to be installed.
    '''

    # * method: create (static)
    @staticmethod
    def create(
            checkpointer_type: str = 'memory',
            config: Dict[str, str] | None = None,
        ) -> Any:
        '''
        Create a LangGraph checkpointer instance.

        :param checkpointer_type: The checkpointer type (memory, sqlite, postgres).
        :type checkpointer_type: str
        :param config: Optional configuration parameters.
        :type config: Dict[str, str] | None
        :return: A LangGraph checkpointer instance.
        :rtype: Any
        '''

        config = config or {}

        # Dispatch to the appropriate factory method.
        if checkpointer_type == 'memory':
            return CheckpointerFactory._create_memory()

        if checkpointer_type == 'sqlite':
            return CheckpointerFactory._create_sqlite(config)

        if checkpointer_type == 'postgres':
            return CheckpointerFactory._create_postgres(config)

        # Unsupported checkpointer type.
        RaiseError.execute(
            error_code=INVALID_CHECKPOINTER_TYPE_ID,
            checkpointer_type=checkpointer_type,
        )

    # * method: _create_memory (static)
    @staticmethod
    def _create_memory() -> Any:
        '''
        Create an in-memory checkpointer.

        :return: A MemorySaver instance.
        :rtype: Any
        '''

        # Import and return MemorySaver.
        from langgraph.checkpoint.memory import MemorySaver
        return MemorySaver()

    # * method: _create_sqlite (static)
    @staticmethod
    def _create_sqlite(config: Dict[str, str]) -> Any:
        '''
        Create a SQLite checkpointer.

        :param config: Configuration with optional 'db_path' key.
        :type config: Dict[str, str]
        :return: A SqliteSaver instance.
        :rtype: Any
        '''

        try:
            from langgraph.checkpoint.sqlite import SqliteSaver
            db_path = config.get('db_path', ':memory:')
            return SqliteSaver.from_conn_string(db_path)
        except ImportError:
            RaiseError.execute(
                error_code=const.INVALID_PROVIDER_ID,
                provider='sqlite',
                message='langgraph-checkpoint-sqlite is not installed. Install with: pip install tiferet-agents[sqlite]',
            )

    # * method: _create_postgres (static)
    @staticmethod
    def _create_postgres(config: Dict[str, str]) -> Any:
        '''
        Create a Postgres checkpointer.

        :param config: Configuration with required 'connection_string' key.
        :type config: Dict[str, str]
        :return: A PostgresSaver instance.
        :rtype: Any
        '''

        try:
            from langgraph.checkpoint.postgres import PostgresSaver
            conn_string = config.get('connection_string', '')
            if not conn_string:
                RaiseError.execute(
                    error_code=INVALID_CHECKPOINTER_TYPE_ID,
                    checkpointer_type='postgres',
                    message='connection_string is required for postgres checkpointer',
                )
            return PostgresSaver.from_conn_string(conn_string)
        except ImportError:
            RaiseError.execute(
                error_code=const.INVALID_PROVIDER_ID,
                provider='postgres',
                message='langgraph-checkpoint-postgres is not installed. Install with: pip install tiferet-agents[postgres]',
            )
