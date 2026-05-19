"""tiferet_agents InMemoryConversationRepository Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.assets.exceptions import TiferetError

from ...assets import constants as const
from ...mappers.conversation import ConversationAggregate, MessageAggregate
from ..conversation import InMemoryConversationRepository

# *** fixtures

# ** fixture: repo
@pytest.fixture
def repo() -> InMemoryConversationRepository:
    '''
    Create a fresh in-memory conversation repository for each test.
    '''

    return InMemoryConversationRepository()


# ** fixture: sample_conversation
@pytest.fixture
def sample_conversation() -> ConversationAggregate:
    '''
    Create a sample conversation aggregate.
    '''

    return ConversationAggregate(
        agent_id='test_agent',
        title='Test Conversation',
    )


# ** fixture: sample_message
@pytest.fixture
def sample_message(sample_conversation) -> MessageAggregate:
    '''
    Create a sample message aggregate.
    '''

    return MessageAggregate(
        conversation_id=sample_conversation.id,
        role='human',
        content='Hello, agent!',
    )


# *** tests

# ** test: exists_empty
def test_exists_empty(repo):
    '''
    Test that exists returns False for an empty store.
    '''

    assert repo.exists('nonexistent') is False


# ** test: save_and_get
def test_save_and_get(repo, sample_conversation):
    '''
    Test saving and retrieving a conversation.
    '''

    # Save the conversation.
    repo.save(sample_conversation)

    # Verify it exists and can be retrieved.
    assert repo.exists(sample_conversation.id) is True
    retrieved = repo.get(sample_conversation.id)
    assert retrieved is sample_conversation
    assert retrieved.agent_id == 'test_agent'
    assert retrieved.title == 'Test Conversation'


# ** test: get_nonexistent
def test_get_nonexistent(repo):
    '''
    Test that get returns None for nonexistent conversations.
    '''

    assert repo.get('nonexistent') is None


# ** test: list_all
def test_list_all(repo):
    '''
    Test listing all conversations.
    '''

    # Save two conversations.
    conv1 = ConversationAggregate(agent_id='agent_a', title='Conv 1')
    conv2 = ConversationAggregate(agent_id='agent_b', title='Conv 2')
    repo.save(conv1)
    repo.save(conv2)

    # List all.
    all_convs = repo.list()
    assert len(all_convs) == 2


# ** test: list_filter_by_agent_id
def test_list_filter_by_agent_id(repo):
    '''
    Test listing conversations filtered by agent_id.
    '''

    # Save conversations for different agents.
    conv1 = ConversationAggregate(agent_id='agent_a', title='Conv 1')
    conv2 = ConversationAggregate(agent_id='agent_b', title='Conv 2')
    conv3 = ConversationAggregate(agent_id='agent_a', title='Conv 3')
    repo.save(conv1)
    repo.save(conv2)
    repo.save(conv3)

    # Filter by agent_a.
    results = repo.list(agent_id='agent_a')
    assert len(results) == 2
    assert all(c.agent_id == 'agent_a' for c in results)


# ** test: list_filter_by_status
def test_list_filter_by_status(repo):
    '''
    Test listing conversations filtered by status.
    '''

    # Save conversations with different statuses.
    conv1 = ConversationAggregate(agent_id='agent_a', title='Conv 1', status='active')
    conv2 = ConversationAggregate(agent_id='agent_a', title='Conv 2', status='archived')
    repo.save(conv1)
    repo.save(conv2)

    # Filter by archived.
    results = repo.list(status='archived')
    assert len(results) == 1
    assert results[0].status == 'archived'


# ** test: delete
def test_delete(repo, sample_conversation):
    '''
    Test deleting a conversation.
    '''

    # Save then delete.
    repo.save(sample_conversation)
    assert repo.exists(sample_conversation.id) is True

    repo.delete(sample_conversation.id)
    assert repo.exists(sample_conversation.id) is False


# ** test: delete_idempotent
def test_delete_idempotent(repo):
    '''
    Test that deleting a nonexistent conversation does not raise.
    '''

    # Should not raise.
    repo.delete('nonexistent')


# ** test: add_message
def test_add_message(repo, sample_conversation, sample_message):
    '''
    Test adding a message to a conversation.
    '''

    # Save the conversation first.
    repo.save(sample_conversation)

    # Add a message.
    repo.add_message(sample_conversation.id, sample_message)

    # Verify the message was added.
    messages = repo.get_messages(sample_conversation.id)
    assert len(messages) == 1
    assert messages[0].role == 'human'
    assert messages[0].content == 'Hello, agent!'


# ** test: add_message_to_nonexistent_conversation
def test_add_message_to_nonexistent_conversation(repo, sample_message):
    '''
    Test that adding a message to a nonexistent conversation raises an error.
    '''

    with pytest.raises(TiferetError) as exc_info:
        repo.add_message('nonexistent', sample_message)

    assert exc_info.value.error_code == const.CONVERSATION_NOT_FOUND_ID


# ** test: get_messages_empty
def test_get_messages_empty(repo, sample_conversation):
    '''
    Test that get_messages returns an empty list for a conversation with no messages.
    '''

    repo.save(sample_conversation)
    assert repo.get_messages(sample_conversation.id) == []


# ** test: get_messages_nonexistent
def test_get_messages_nonexistent(repo):
    '''
    Test that get_messages returns an empty list for a nonexistent conversation.
    '''

    assert repo.get_messages('nonexistent') == []
