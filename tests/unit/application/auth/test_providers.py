from assertpy.assertpy import assert_that

from movie_nerd.infrastructure.auth.password_hasher import Pbkdf2PasswordHasher
from movie_nerd.infrastructure.auth.token_service import HmacTokenService
from movie_nerd.application.auth.errors import InvalidToken


def test_password_hasher_hash_and_verify() -> None:
    hasher = Pbkdf2PasswordHasher(iterations=1_000)
    hashed = hasher.hash_password(plain_password="secret")

    assert_that(hashed).is_not_equal_to("secret")
    assert_that(hasher.verify_password(plain_password="secret", password_hash=hashed)).is_true()
    assert_that(hasher.verify_password(plain_password="wrong", password_hash=hashed)).is_false()


def test_token_service_sign_and_verify() -> None:
    service = HmacTokenService(secret="test-secret", expires_in_seconds=60)
    token = service.create_token(subject="subj-1")
    assert_that(service.verify_token(token=token)).is_equal_to("subj-1")

    payload_b64, sig_b64 = token.split(".", 1)
    tampered = payload_b64 + "." + sig_b64[:-1] + ("A" if sig_b64[-1] != "A" else "B")
    try:
        service.verify_token(token=tampered)
    except InvalidToken:
        assert_that(True).is_true()
    else:
        assert_that(False).is_true()

