from ddd.application import CommandHandler, Command
from ddd import Identity, Clock

from movie_nerd.domain import Chat
from movie_nerd.domain.service import ChatRepository


class SendMessageCommand(Command):
    def __init__(self, chat_id: Identity, content: str) -> None:
        self.chat_id = chat_id
        self.content = content


class SendMessageCommandHandler(CommandHandler):
    def __init__(self, chat_repository: ChatRepository, clock: Clock) -> None:
        self.__chat_repository = chat_repository
        self.__clock = clock

    def handle(self, command: SendMessageCommand) -> None:
        chat: Chat = self.__chat_repository.get(command.chat_id)
        chat.send_user_message(command.content, self.__clock.now())
        self.__chat_repository.save(chat)