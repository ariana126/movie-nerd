from ddd.domain.service.repository import AggregateRootType

from movie_nerd.domain import User
from movie_nerd.domain.service import UserRepository
from movie_nerd.infrastructure.persistence.sql_alchemy.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyUserRepository(UserRepository, SQLAlchemyBaseRepository):
    @property
    def entity(self) -> type[AggregateRootType]:
        return User