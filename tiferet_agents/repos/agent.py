"""tiferet_agents Agent YAML Repository"""

# *** imports

# ** core
from typing import List, Optional

# ** app
from tiferet.utils import Yaml

from ..interfaces.agent import AgentService
from ..mappers.agent import AgentConfigurationAggregate, AgentConfigurationYamlObject

# *** repos

# ** repo: agent_yaml_repository
class AgentYamlRepository(AgentService):
    '''
    YAML-backed repository for agent configurations.

    Reads and writes agent configurations from a YAML file following
    the standard Tiferet repository pattern.
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: encoding
    encoding: str

    # * init
    def __init__(self, agent_yaml_file: str = 'app/configs/agent.yml', encoding: str = 'utf-8'):
        '''
        Initialize the agent YAML repository.

        :param agent_yaml_file: Path to the YAML configuration file.
        :type agent_yaml_file: str
        :param encoding: File encoding.
        :type encoding: str
        '''

        # Set the YAML file path and encoding.
        self.yaml_file = agent_yaml_file
        self.encoding = encoding

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if an agent configuration exists by ID.

        :param id: The agent identifier.
        :type id: str
        :return: True if the agent exists.
        :rtype: bool
        '''

        # Load and check.
        return self.get(id) is not None

    # * method: get
    def get(self, id: str) -> Optional[AgentConfigurationAggregate]:
        '''
        Retrieve an agent configuration by ID.

        :param id: The agent identifier.
        :type id: str
        :return: The agent aggregate, or None.
        :rtype: AgentConfigurationAggregate | None
        '''

        # Load all agents and find by ID.
        agents = self._load_agents()
        return agents.get(id)

    # * method: list
    def list(self) -> List[AgentConfigurationAggregate]:
        '''
        List all agent configurations.

        :return: A list of agent aggregates.
        :rtype: List[AgentConfigurationAggregate]
        '''

        # Load and return all agents.
        return list(self._load_agents().values())

    # * method: save
    def save(self, agent: AgentConfigurationAggregate) -> None:
        '''
        Save or update an agent configuration.

        :param agent: The agent aggregate to save.
        :type agent: AgentConfigurationAggregate
        '''

        # Convert to YAML object.
        yaml_obj = AgentConfigurationYamlObject.from_model(agent)
        data = yaml_obj.to_primitive('to_data.yaml')

        # Save to the YAML file under agents.<id>.
        with Yaml(self.yaml_file, mode='a', encoding=self.encoding) as y:
            y.save(data, data_path=f'agents.{agent.id}')

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete an agent configuration by ID.

        :param id: The agent identifier.
        :type id: str
        '''

        # Load current data, remove the agent, and rewrite.
        with Yaml(self.yaml_file, mode='a', encoding=self.encoding) as y:
            y.save(None, data_path=f'agents.{id}')

    # * method: _load_agents
    def _load_agents(self) -> dict:
        '''
        Load all agent configurations from the YAML file.

        :return: A dict mapping agent IDs to aggregates.
        :rtype: dict
        '''

        # Load the YAML data.
        try:
            raw = Yaml(self.yaml_file, mode='r', encoding=self.encoding).load(
                start_node=lambda data: data.get('agents', {}),
            )
        except Exception:
            return {}

        # Map each entry to an aggregate.
        agents = {}
        for agent_id, agent_data in (raw or {}).items():
            if agent_data is None:
                continue
            agent_data['id'] = agent_id
            yaml_obj = AgentConfigurationYamlObject.model_validate(agent_data)
            agents[agent_id] = yaml_obj.map()

        # Return the agents dict.
        return agents
