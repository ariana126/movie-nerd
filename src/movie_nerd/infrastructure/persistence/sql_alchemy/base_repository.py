from abc import ABC, abstractmethod

from ddd import EntityRepository, AggregateRoot, Identity
from ddd.domain.service.repository import AggregateRootType
from sqlalchemy.orm.session import Session

from movie_nerd.infrastructure.persistence.sql_alchemy.connection import Connection


class SQLAlchemyBaseRepository(EntityRepository, ABC):
    def __init__(self, connection: Connection):
        self.connection = connection

    def find(self, _id: Identity) -> AggregateRootType | None:
        return self.connection.get_session().get(self.entity, _id)

    def save(self, entity: AggregateRoot) -> None:
        session: Session = self.connection.get_session()
        session.add(entity)
        session.commit()

    @property
    @abstractmethod
    def entity(self) -> type[AggregateRootType]:
        pass