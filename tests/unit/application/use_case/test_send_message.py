from datetime import datetime

from assertpy.assertpy import assert_that
from ddd.test_double import StubClock
from ddd import Identity
from ddd.domain.service import EntityNotFound

from movie_nerd.application.use_case.send_message import SendMessageCommand, SendMessageCommandHandler
from movie_nerd.domain import Chat, ChatMessage
from movie_nerd.domain.chat_events import UserSentMessage
from tests.test_double import InMemoryChatRepository

chat_repository = InMemoryChatRepository()
clock = StubClock(datetime(2025, 3, 30, 9, 30, 0))

def _start_chat() -> Chat:
    chat = Chat.start(Identity.from_string('dummy-user-id'), clock.now())
    chat_repository.save(chat)
    chat.release_events()
    return chat


def test_a_message_is_sent_to_an_existing_chat():
    command = SendMessageCommand(Identity.from_string('not-existed-chat-id'), 'dummy-content')
    sut = SendMessageCommandHandler(chat_repository, clock)

    try:
        sut.handle(command)

    except Exception as error:
        assert_that(error).is_instance_of(EntityNotFound)
    chat_repository.assert_database_is_empty()


def test_a_new_message_is_saved_in_the_chat():
    chat = _start_chat()
    command = SendMessageCommand(chat.id, 'dummy-content')
    sut = SendMessageCommandHandler(chat_repository, clock)

    sut.handle(command)

    persisted_chat: Chat = chat_repository.find(chat.id)
    assert_that(persisted_chat).is_not_none()
    assert_that(persisted_chat.messages).is_length(1)
    persisted_message: ChatMessage = persisted_chat.messages[0]
    assert_that(persisted_message.is_from_user).is_true()
    assert_that(persisted_message.content).is_equal_to(command.content)
    assert_that(persisted_message.sent_at).is_equal_to(clock.now())


def test_when_a_new_message_sent_its_domain_event_captured():
    chat = _start_chat()
    command = SendMessageCommand(chat.id, 'dummy-content')
    sut = SendMessageCommandHandler(chat_repository, clock)

    sut.handle(command)

    events = chat.release_events()
    assert_that(events).is_length(1)
    assert_that(events[0]).is_instance_of(UserSentMessage)