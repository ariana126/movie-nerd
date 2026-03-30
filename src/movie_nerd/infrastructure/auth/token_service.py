from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

from movie_nerd.application.auth.errors import InvalidToken


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value + padding)


class HmacTokenService:
    """
    Minimal signed token: payload is JSON, signature is HMAC-SHA256 over the
    base64url-encoded payload.
    """

    def __init__(self, *, secret: str, expires_in_seconds: int = 3600) -> None:
        self._secret = secret
        self._expires_in_seconds = expires_in_seconds

    def create_token(self, *, subject: str) -> str:
        now = int(time.time())
        payload = {"sub": subject, "iat": now, "exp": now + self._expires_in_seconds}
        payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        payload_b64 = _b64url_encode(payload_json)

        signature = hmac.new(
            self._secret.encode("utf-8"),
            payload_b64.encode("ascii"),
            hashlib.sha256,
        ).digest()
        signature_b64 = _b64url_encode(signature)

        return f"{payload_b64}.{signature_b64}"

    def verify_token(self, *, token: str) -> str:
        try:
            payload_b64, signature_b64 = token.split(".", 1)
        except ValueError as exc:
            raise InvalidToken() from exc

        expected_signature = hmac.new(
            self._secret.encode("utf-8"),
            payload_b64.encode("ascii"),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(_b64url_encode(expected_signature), signature_b64):
            raise InvalidToken()

        payload_json = _b64url_decode(payload_b64)
        payload = json.loads(payload_json.decode("utf-8"))
        try:
            exp = int(payload["exp"])
            subject = str(payload["sub"])
        except Exception as exc:  # noqa: BLE001 - normalize token errors
            raise InvalidToken() from exc

        if int(time.time()) >= exp:
            raise InvalidToken()
        return subject

