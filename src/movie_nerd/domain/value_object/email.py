from __future__ import annotations

import re


class InvalidEmail(ValueError):
    pass


_EMAIL_RE = re.compile(
    # pragmatic validation (not RFC-perfect), but blocks common invalid cases
    r"^(?=.{3,254}$)(?=.{1,64}@)"
    r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@"
    r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z0-9]{2,63}$",
    re.IGNORECASE,
)


class Email:
    def __init__(self, value: str):
        normalized = value.strip().lower()
        if not _EMAIL_RE.match(normalized):
            raise InvalidEmail(f"Invalid email: {value!r}")
        self.__value = normalized

    @classmethod
    def from_string(cls, value: str) -> "Email":
        return Email(value)

    @property
    def as_string(self) -> str:
        return self.__value

    def __str__(self) -> str:
        return self.__value

    def __repr__(self) -> str:
        return f"Email({self.__value!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Email) and other.__value == self.__value

    def __hash__(self) -> int:
        return hash(self.__value)

