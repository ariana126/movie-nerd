from assertpy.assertpy import assert_that
from fastapi.testclient import TestClient

from movie_nerd.application.auth.auth_service import AuthService
from movie_nerd.infrastructure.auth import HmacTokenService, InMemoryUserStore, Pbkdf2PasswordHasher
from movie_nerd.infrastructure.http.app_factory import create_app


def _make_app(*, secret: str = "test-secret") -> tuple[TestClient, AuthService, InMemoryUserStore]:
    user_store = InMemoryUserStore()
    password_hasher = Pbkdf2PasswordHasher(iterations=1_000)
    token_service = HmacTokenService(secret=secret, expires_in_seconds=60)
    auth_service = AuthService(
        user_store=user_store,
        password_hasher=password_hasher,
        token_service=token_service,
    )
    app = create_app(auth_service=auth_service)
    client = TestClient(app)
    return client, auth_service, user_store


def test_register_login_and_me_flow() -> None:
    client, _, store = _make_app()

    email = "User@Example.com"
    password = "dummy-password"
    first_name = "UserFirst"
    last_name = "UserLast"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        },
    )
    assert_that(register_response.status_code).is_equal_to(201)

    stored_user = store.get_by_email(email=email)
    assert_that(stored_user).is_not_none()
    assert_that(stored_user.password).is_not_equal_to(password)
    assert_that(stored_user.first_name).is_equal_to(first_name)
    assert_that(stored_user.last_name).is_equal_to(last_name)

    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert_that(login_response.status_code).is_equal_to(200)
    token = login_response.json()["token"]
    assert_that(token).is_not_empty()

    me_response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert_that(me_response.status_code).is_equal_to(200)
    assert_that(me_response.json()["email"]).is_equal_to(email.lower())


def test_register_duplicate_returns_409() -> None:
    client, _, _ = _make_app()
    email = "dup@example.com"
    password = "dummy-password"
    first_name = "DupeFirst"
    last_name = "DupeLast"

    response1 = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        },
    )
    assert_that(response1.status_code).is_equal_to(201)

    response2 = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        },
    )
    assert_that(response2.status_code).is_equal_to(409)


def test_login_wrong_password_returns_401() -> None:
    client, _, _ = _make_app()
    email = "wrongpass@example.com"
    first_name = "WrongFirst"
    last_name = "WrongLast"

    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "correct",
            "first_name": first_name,
            "last_name": last_name,
        },
    )

    response = client.post("/auth/login", json={"email": email, "password": "wrong"})
    assert_that(response.status_code).is_equal_to(401)


def test_me_with_invalid_token_returns_401() -> None:
    client, _, _ = _make_app()
    response = client.get("/me", headers={"Authorization": "Bearer invalid-token"})
    assert_that(response.status_code).is_equal_to(401)

