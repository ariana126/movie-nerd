from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ddd import Identity

from movie_nerd.application.auth.errors import (
    InvalidCredentials,
    InvalidToken,
    UserAlreadyExists,
)
from movie_nerd.domain import User


class TokenService(Protocol):
    def create_token(self, *, subject: str) -> str: ...

    def verify_token(self, *, token: str) -> str: ...


class PasswordHasher(Protocol):
    def hash_password(self, *, plain_password: str) -> str: ...

    def verify_password(self, *, plain_password: str, password_hash: str) -> bool: ...


class UserStore(Protocol):
    def get_by_id(self, *, user_id: Identity) -> User | None: ...

    def get_by_email(self, *, email: str) -> User | None: ...

    def save(self, *, user: User) -> None: ...


def _normalize_email(email: str) -> str:
    return email.strip().lower()


@dataclass(frozen=True)
class AuthService:
    user_store: UserStore
    password_hasher: PasswordHasher
    token_service: TokenService

    def register(
        self,
        *,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
    ) -> None:
        normalized_email = _normalize_email(email)
        if self.user_store.get_by_email(email=normalized_email) is not None:
            raise UserAlreadyExists()

        password_hash = self.password_hasher.hash_password(plain_password=password)
        self.user_store.save(
            user=User(
                Identity.new(),
                email=normalized_email,
                password=password_hash,
                first_name=first_name,
                last_name=last_name,
            )
        )

    def login(self, *, email: str, password: str) -> str:
        normalized_email = _normalize_email(email)
        user = self.user_store.get_by_email(email=normalized_email)
        if user is None or not self.password_hasher.verify_password(
            plain_password=password,
            password_hash=user.password,
        ):
            raise InvalidCredentials()

        token = self.token_service.create_token(subject=user.id.as_string)
        return token

    def get_user_from_token(self, *, token: str) -> User:
        try:
            subject = self.token_service.verify_token(token=token)
        except Exception as exc:  # noqa: BLE001 - normalize provider errors
            raise InvalidToken() from exc

        user = self.user_store.get_by_id(user_id=Identity.from_string(subject))
        if user is None:
            raise InvalidToken()
        return user

