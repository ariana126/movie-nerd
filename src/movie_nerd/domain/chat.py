from datetime import datetime
from enum import Enum

from ddd import AggregateRoot, Identity, Entity

from .chat_events import UserSentMessage, ChatStarted


class Sender(Enum):
    USER = "USER"
    BOT = "BOT"


class ChatMessage(Entity):
    def __init__(self, _id: Identity, sender: Sender, content: str, sent_at: datetime):
        super().__init__(_id)
        self.__sender = sender
        self.__content = content
        self.__sent_at = sent_at

    @property
    def content(self) -> str:
        return self.__content

    @property
    def is_from_user(self) -> bool:
        return self.__sender is Sender.USER

    @property
    def sent_at(self) -> datetime:
        return self.__sent_at


class ChatStatus(Enum):
    STARTED = 'STARTED'


class Chat(AggregateRoot):
    def __init__(self, _id: Identity, user_id: Identity, messages: list[ChatMessage], status: ChatStatus, started_at: datetime):
        super().__init__(_id)
        self.__user_id = user_id
        self.__messages = messages
        self.__status = status
        self.__started_at = started_at

    @staticmethod
    def start(user_id: Identity, time: datetime) -> 'Chat':
        chat = Chat(Identity.new(), user_id, [], ChatStatus.STARTED, time)
        chat.signal_start()
        return chat
    # TODO: Should be fixed in underpy Encapsulated class
    def signal_start(self) -> None:
        self._record_that(ChatStarted(self._id))

    def send_user_message(self, content: str, time: datetime):
        message = ChatMessage(Identity.new(), Sender.USER, content, time)
        self.__messages.append(message)
        self._record_that(UserSentMessage(message.id, self._id))

    def send_bot_message(self, content: str, time: datetime):
        self.__messages.append(ChatMessage(Identity.new(), Sender.BOT, content, time))

    @property
    def is_started(self) -> bool:
        return self.__status is ChatStatus.STARTED

    @property
    def messages(self) -> list[ChatMessage]:
        return self.__messages

    @property
    def started_at(self) -> datetime:
        return self.__started_at