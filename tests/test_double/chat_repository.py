from ddd.test_double import SpyEntityRepository

from movie_nerd.domain.service import ChatRepository


class InMemoryChatRepository(ChatRepository, SpyEntityRepository):
    pass