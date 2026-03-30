from __future__ import annotations

from abc import ABCMeta

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeMeta, declarative_base
from sqlalchemy.sql.type_api import TypeDecorator

from ddd import Identity
from movie_nerd.domain.value_object import Email


class IdentityType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value: Identity, dialect):
        return value.as_string

    def process_result_value(self, value: str, dialect):
        return Identity.from_string(value)


class EmailType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value: Email, dialect):
        return value.as_string

    def process_result_value(self, value: str, dialect):
        return Email.from_string(value)


class DeclarativeABCMeta(DeclarativeMeta, ABCMeta):
    """
    Combine SQLAlchemy's declarative metaclass with ABCMeta.

    This allows ORM entities to also inherit from `ddd.AggregateRoot`
    (which uses ABCMeta) without metaclass conflicts.
    """


Base = declarative_base(metaclass=DeclarativeABCMeta)

