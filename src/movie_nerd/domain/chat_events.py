from ddd import DomainEvent, Identity


class ChatStarted(DomainEvent):
    def __init__(self, chat_id: Identity):
        self.chat_id = chat_id


class UserSentMessage(DomainEvent):
    def __init__(self, message_id: Identity, chat_id: Identity):
        self.message_id = message_id
        self.chat_id = chat_id
