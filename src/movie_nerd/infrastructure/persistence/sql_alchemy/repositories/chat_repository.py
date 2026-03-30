from ddd.domain.service.repository import AggregateRootType

from movie_nerd.domain import Chat
from movie_nerd.domain.service import ChatRepository
from movie_nerd.infrastructure.persistence.sql_alchemy.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyChatRepository(ChatRepository, SQLAlchemyBaseRepository):
    @property
    def entity(self) -> type[AggregateRootType]:
        return Chat