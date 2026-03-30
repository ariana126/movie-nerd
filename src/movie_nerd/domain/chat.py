from datetime import datetime
from enum import Enum

from ddd import AggregateRoot, Identity, Entity

from .chat_events import UserSentMessage, ChatStarted
from movie_nerd.infrastructure.persistence.sql_alchemy.orm import Base, IdentityType

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Sender(Enum):
    USER = "USER"
    BOT = "BOT"


class ChatMessage(Base, Entity):
    __tablename__ = "chat_message"

    _id: Mapped[Identity] = mapped_column("id", IdentityType, primary_key=True)
    chat_id: Mapped[Identity] = mapped_column(
        "chat_id",
        IdentityType,
        ForeignKey("chat.id", ondelete="CASCADE"),
        nullable=False,
    )
    sender: Mapped[Sender] = mapped_column(
        "sender",
        SAEnum(Sender, name="chat_message_sender"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column("content", Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        "sent_at",
        DateTime(timezone=False),
        nullable=False,
    )

    chat: Mapped["Chat"] = relationship(back_populates="messages")

    def __init__(self, _id: Identity, sender: Sender, content: str, sent_at: datetime):
        # Can't use super() here: SQLAlchemy's declarative base provides a
        # kwargs-only constructor, while an Entity expects an id.
        Entity.__init__(self, _id)
        self.sender = sender
        self.content = content
        self.sent_at = sent_at

    @property
    def is_from_user(self) -> bool:
        return self.sender is Sender.USER


class ChatStatus(Enum):
    STARTED = 'STARTED'


class Chat(Base, AggregateRoot):
    __tablename__ = "chat"

    _id: Mapped[Identity] = mapped_column("id", IdentityType, primary_key=True)
    user_id: Mapped[Identity] = mapped_column(
        "user_id",
        IdentityType,
        ForeignKey("user.id"),
        nullable=False,
    )
    status: Mapped[ChatStatus] = mapped_column(
        "status",
        SAEnum(ChatStatus, name="chat_status"),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        "started_at",
        DateTime(timezone=False),
        nullable=False,
    )

    messages: Mapped[list[ChatMessage]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="ChatMessage.sent_at",
        lazy="selectin",
    )

    def __init__(self, _id: Identity, user_id: Identity, messages: list[ChatMessage], status: ChatStatus, started_at: datetime):
        # Can't use super() here: SQLAlchemy's declarative base provides a
        # kwargs-only constructor, while AggregateRoot expects an id.
        AggregateRoot.__init__(self, _id)
        self.user_id = user_id
        self.messages = messages
        self.status = status
        self.started_at = started_at

    @staticmethod
    def start(user_id: Identity, time: datetime) -> 'Chat':
        chat = Chat(Identity.new(), user_id, [], ChatStatus.STARTED, time)
        chat._record_that(ChatStarted(chat.id))
        return chat

    def send_user_message(self, content: str, time: datetime):
        message = ChatMessage(Identity.new(), Sender.USER, content, time)
        self.messages.append(message)
        self._record_that(UserSentMessage(message.id, self._id))

    def send_bot_message(self, content: str, time: datetime):
        self.messages.append(ChatMessage(Identity.new(), Sender.BOT, content, time))

    @property
    def is_started(self) -> bool:
        return self.status is ChatStatus.STARTED