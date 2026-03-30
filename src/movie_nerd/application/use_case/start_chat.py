from ddd.application import Command, CommandHandler
from ddd import Identity, Clock

from movie_nerd.domain import Chat
from movie_nerd.domain.service import ChatRepository


class StartChatCommand(Command):
    def __init__(self, user_id: Identity) -> None:
        self.user_id = user_id


class StartChatCommandHandler(CommandHandler):
    def __init__(self, chat_repository: ChatRepository, clock: Clock) -> None:
        self.__chat_repository = chat_repository
        self.__clock = clock

    def handle(self, command: StartChatCommand) -> Chat:
        chat = Chat.start(command.user_id, self.__clock.now())
        self.__chat_repository.save(chat)
        return chat