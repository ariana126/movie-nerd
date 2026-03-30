from __future__ import annotations

import base64
import hashlib
import hmac
import os


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value + padding)


class Pbkdf2PasswordHasher:
    """
    Password hashing using PBKDF2-HMAC-SHA256.

    Format: pbkdf2_sha256$<iterations>$<salt_b64url>$<hash_b64url>
    """

    def __init__(
        self,
        *,
        iterations: int = 100_000,
        salt_bytes: int = 16,
        hash_bytes: int = 32,
    ) -> None:
        self._iterations = iterations
        self._salt_bytes = salt_bytes
        self._hash_bytes = hash_bytes

    def hash_password(self, *, plain_password: str) -> str:
        plain_password_bytes = plain_password.encode("utf-8")
        salt = os.urandom(self._salt_bytes)
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password_bytes,
            salt,
            self._iterations,
            dklen=self._hash_bytes,
        )
        return "pbkdf2_sha256$" + "$".join(
            [
                str(self._iterations),
                _b64url_encode(salt),
                _b64url_encode(dk),
            ]
        )

    def verify_password(self, *, plain_password: str, password_hash: str) -> bool:
        try:
            algo, iterations_s, salt_b64, hash_b64 = password_hash.split("$", 3)
            if algo != "pbkdf2_sha256":
                return False
            iterations = int(iterations_s)
            salt = _b64url_decode(salt_b64)
            expected_hash = _b64url_decode(hash_b64)

            dk = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt,
                iterations,
                dklen=len(expected_hash),
            )
            return hmac.compare_digest(dk, expected_hash)
        except Exception:
            # Keep auth behavior consistent: wrong hash => invalid credentials.
            return False

