from datetime import datetime

from assertpy.assertpy import assert_that
from ddd.test_double import StubClock
from ddd import Identity

from movie_nerd.application.use_case.start_chat import StartChatCommandHandler, StartChatCommand
from movie_nerd.domain import Chat
from movie_nerd.domain.chat_events import ChatStarted
from tests.test_double import InMemoryChatRepository

chat_repository = InMemoryChatRepository()
clock = StubClock(datetime(2025, 3, 30, 9, 30, 0))


def test_started_chat_is_saved():
    command = StartChatCommand(Identity.from_string('dummy-user-id'))
    sut = StartChatCommandHandler(chat_repository, clock)

    chat = sut.handle(command)

    persisted_chat: Chat = chat_repository.find(chat.id)
    assert_that(persisted_chat.id).is_equal_to(chat.id)
    assert_that(persisted_chat.is_started).is_true()
    assert_that(persisted_chat.messages).is_empty()
    assert_that(persisted_chat.started_at).is_equal_to(clock.now())


def test_starting_chat_domain_event_is_captured():
    command = StartChatCommand(Identity.from_string('dummy-user-id'))
    sut = StartChatCommandHandler(chat_repository, clock)

    chat = sut.handle(command)

    events = chat.release_events()
    assert_that(events).is_length(1)
    assert_that(events[0]).is_instance_of(ChatStarted)