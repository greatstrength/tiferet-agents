"""tiferet_agents Conversation Domain Tests"""

# *** imports

# ** infra

# ** app
from ..conversation import Conversation, Message

# *** tests

# ** test: message_defaults
def test_message_defaults():
    '''
    Test that Message auto-derives id and created_at.
    '''

    # Create a message with required fields only.
    msg = Message(conversation_id='conv-1', role='human', content='Hello')

    # Assert defaults.
    assert msg.id  # UUID generated
    assert msg.conversation_id == 'conv-1'
    assert msg.role == 'human'
    assert msg.content == 'Hello'
    assert msg.tool_calls == []
    assert msg.tool_call_id is None
    assert msg.created_at


# ** test: message_tool_role
def test_message_tool_role():
    '''
    Test creating a tool-role message with tool_call_id.
    '''

    # Create a tool response message.
    msg = Message(
        conversation_id='conv-1',
        role='tool',
        content='Result: 42',
        tool_call_id='call_abc123',
    )

    # Assert fields.
    assert msg.role == 'tool'
    assert msg.tool_call_id == 'call_abc123'


# ** test: conversation_defaults
def test_conversation_defaults():
    '''
    Test that Conversation auto-derives id, thread_id, and timestamps.
    '''

    # Create with required agent_id only.
    conv = Conversation(agent_id='agent-1')

    # Assert defaults.
    assert conv.id  # UUID generated
    assert conv.agent_id == 'agent-1'
    assert conv.thread_id  # UUID generated
    assert conv.status == 'active'
    assert conv.messages == []
    assert conv.created_at
    assert conv.updated_at


# ** test: conversation_with_messages
def test_conversation_with_messages():
    '''
    Test creating a conversation with pre-populated messages.
    '''

    # Create with messages.
    conv = Conversation(
        agent_id='agent-1',
        messages=[
            Message(conversation_id='conv-1', role='human', content='Hi'),
            Message(conversation_id='conv-1', role='ai', content='Hello!'),
        ],
    )

    # Assert message count.
    assert conv.message_count() == 2
    assert conv.messages[0].role == 'human'
    assert conv.messages[1].role == 'ai'
