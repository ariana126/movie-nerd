from datetime import datetime

from assertpy.assertpy import assert_that
from ddd import Identity
from pydm import ServiceContainer
from ddd.test_double import StubClock

from movie_nerd.domain import Chat, User
from movie_nerd.domain.service import ChatRepository

service_container = ServiceContainer.get_instance()
clock = StubClock(datetime(2025, 3, 30, 9, 30, 0))


def test_saved_chat_will_be_returned_with_entity(seeded_user: User):
    chat = Chat.start(seeded_user.id, clock.now())
    sut = service_container.get_service(ChatRepository)
    sut.save(chat)

    persisted_chat = sut.find(chat.id)

    assert_that(persisted_chat).is_not_none()
    assert_that(persisted_chat).is_equal_to(chat)


def test_chat_user_should_be_existed_in_db():
    chat = Chat.start(Identity.from_string('not-existed-user-id'), clock.now())
    sut = service_container.get_service(ChatRepository)

    try:
        sut.save(chat)
    except Exception as e:
        pass
    persisted_chat = sut.find(chat.id)
    assert_that(persisted_chat).is_none()

def test_chat_messages_are_persisted_with_it(seeded_user: User):
    chat = Chat.start(seeded_user.id, clock.now())
    message_content = 'dummy-content'
    chat.send_user_message(message_content, clock.now())
    sut = service_container.get_service(ChatRepository)
    sut.save(chat)

    persisted_chat: Chat = sut.find(chat.id)

    assert_that(persisted_chat).is_equal_to(chat)
    assert_that(persisted_chat.messages).is_length(1)
    assert_that(persisted_chat.messages[0].content).is_equal_to(message_content)
    assert_that(persisted_chat.messages[0].sent_at).is_equal_to(clock.now())
