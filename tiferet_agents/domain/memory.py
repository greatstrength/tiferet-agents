"""tiferet_agents Memory Domain"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

# ** infra
from pydantic import Field, model_validator

# ** app
from tiferet.domain import DomainObject

# *** models

# ** model: memory_fact
class MemoryFact(DomainObject):
    '''
    A triple-shaped memory fact that an agent has learned.

    Facts are stored as subject/predicate/object triples with a
    confidence score and source provenance.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='UUID string uniquely identifying this fact.',
    )

    # * attribute: namespace_id
    namespace_id: str = Field(
        ...,
        description='ID of the memory namespace this fact belongs to.',
    )

    # * attribute: subject
    subject: str = Field(
        ...,
        description='The subject of the fact triple (e.g., "user").',
    )

    # * attribute: predicate
    predicate: str = Field(
        ...,
        description='The predicate of the fact triple (e.g., "prefers").',
    )

    # * attribute: object
    object: str = Field(
        ...,
        description='The object of the fact triple (e.g., "Python").',
    )

    # * attribute: confidence
    confidence: float = Field(
        default=1.0,
        description='Confidence score for this fact (0.0 to 1.0).',
    )

    # * attribute: source
    source: str = Field(
        default='system',
        description='Provenance of this fact (conversation_id or "system").',
    )

    # * attribute: created_at
    created_at: str = Field(
        ...,
        description='ISO 8601 creation timestamp.',
    )

    # * method: _derive_defaults (validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_defaults(cls, data: Any) -> Any:
        '''
        Derive default values for id and created_at when absent.

        :param data: The raw input data.
        :type data: Any
        :return: The augmented input data.
        :rtype: Any
        '''

        # Only mutate dict-shaped inputs.
        if not isinstance(data, dict):
            return data
        data = dict(data)

        # Generate a UUID if id is not provided.
        if not data.get('id'):
            data['id'] = str(uuid4())

        # Set timestamp if not provided.
        if not data.get('created_at'):
            data['created_at'] = datetime.now(timezone.utc).isoformat()

        # Return the augmented data.
        return data

    # * method: to_text
    def to_text(self) -> str:
        '''
        Render the fact as a natural language string for embedding.

        :return: The fact as text.
        :rtype: str
        '''

        # Return the triple as a readable string.
        return f'{self.subject} {self.predicate} {self.object}'


# ** model: memory_namespace
class MemoryNamespace(DomainObject):
    '''
    A namespace grouping memory facts for an agent.

    Each agent may have one or more namespaces to organize facts
    by topic or context.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='UUID string uniquely identifying this namespace.',
    )

    # * attribute: agent_id
    agent_id: str = Field(
        ...,
        description='ID of the agent this namespace belongs to.',
    )

    # * attribute: name
    name: str = Field(
        default='default',
        description='Human-readable namespace name.',
    )

    # * attribute: description
    description: str = Field(
        default='',
        description='Optional description of this namespace.',
    )

    # * attribute: created_at
    created_at: str = Field(
        ...,
        description='ISO 8601 creation timestamp.',
    )

    # * method: _derive_defaults (validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_defaults(cls, data: Any) -> Any:
        '''
        Derive default values for id and created_at when absent.

        :param data: The raw input data.
        :type data: Any
        :return: The augmented input data.
        :rtype: Any
        '''

        # Only mutate dict-shaped inputs.
        if not isinstance(data, dict):
            return data
        data = dict(data)

        # Generate a UUID if id is not provided.
        if not data.get('id'):
            data['id'] = str(uuid4())

        # Set timestamp if not provided.
        if not data.get('created_at'):
            data['created_at'] = datetime.now(timezone.utc).isoformat()

        # Return the augmented data.
        return data
