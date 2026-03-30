from __future__ import annotations

from typing import Dict

from ddd import Identity

from movie_nerd.application.auth.auth_service import UserStore
from movie_nerd.domain import User
from movie_nerd.infrastructure.persistence.sql_alchemy.connection import Connection

try:
    from sqlalchemy import select
except Exception:  # pragma: no cover - unit tests don't require SQLAlchemy import
    select = None  # type: ignore[assignment]


class InMemoryUserStore(UserStore):
    def __init__(self) -> None:
        self._by_id: Dict[str, User] = {}
        self._by_email: Dict[str, User] = {}

    def get_by_id(self, *, user_id: Identity) -> User | None:
        return self._by_id.get(user_id.as_string)

    def get_by_email(self, *, email: str) -> User | None:
        return self._by_email.get(email.strip().lower())

    def save(self, *, user: User) -> None:
        self._by_id[user.id.as_string] = user
        self._by_email[user.email] = user


class SQLAlchemyUserStore(UserStore):
    def __init__(self, *, connection: Connection) -> None:
        self._connection = connection

    def get_by_id(self, *, user_id: Identity) -> User | None:
        session = self._connection.get_session()
        return session.get(User, user_id)

    def get_by_email(self, *, email: str) -> User | None:
        if select is None:  # pragma: no cover
            raise RuntimeError("SQLAlchemy not available")
        session = self._connection.get_session()
        stmt = select(User).where(User.email == email)
        return session.execute(stmt).scalar_one_or_none()

    def save(self, *, user: User) -> None:
        session = self._connection.get_session()
        session.add(user)
        session.commit()

