from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ddd import AggregateRoot, Identity

from movie_nerd.infrastructure.persistence.sql_alchemy.orm import Base, IdentityType


class User(Base, AggregateRoot):
    __tablename__ = "user"

    _id: Mapped[Identity] = mapped_column("id", IdentityType, primary_key=True)
    first_name: Mapped[str] = mapped_column("first_name", String, nullable=False)
    last_name: Mapped[str] = mapped_column("last_name", String, nullable=False)
    email: Mapped[str] = mapped_column(
        "email",
        String,
        nullable=False,
        unique=True,
        index=True,
    )
    # Stored as a hashed value (e.g. pbkdf2 string). The app is responsible for hashing.
    password: Mapped[str] = mapped_column("password", Text, nullable=False)

    def __init__(
        self,
        _id: Identity,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
    ):
        # Can't use super() here: SQLAlchemy's declarative base provides a
        # kwargs-only constructor, while AggregateRoot expects an id.
        AggregateRoot.__init__(self, _id)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email.strip().lower()
        self.password = password
