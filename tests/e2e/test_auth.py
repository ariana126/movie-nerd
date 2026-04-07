from fastapi.testclient import TestClient
from assertpy import assert_that


def test_registered_user_can_login_and_view_their_profile(http_client: TestClient) -> None:
    SUT = http_client
    SUT.post("/auth/register", json={
        "email": "alice@example.com",
        "password": "secret123",
        "first_name": "Alice",
        "last_name": "Smith",
    })
    login_response = SUT.post("/auth/login", json={
        "email": "alice@example.com",
        "password": "secret123",
    })
    token = login_response.json()["token"]

    response = SUT.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert_that(response.status_code).is_equal_to(200)
    assert_that(response.json()).is_equal_to({
        "email": "alice@example.com",
        "first_name": "Alice",
        "last_name": "Smith",
    })


def test_registering_with_a_taken_email_is_rejected(http_client: TestClient) -> None:
    SUT = http_client
    SUT.post("/auth/register", json={
        "email": "bob@example.com",
        "password": "pass1",
        "first_name": "Bob",
        "last_name": "Jones",
    })

    response = SUT.post("/auth/register", json={
        "email": "bob@example.com",
        "password": "pass2",
        "first_name": "Bob",
        "last_name": "Jones",
    })

    assert_that(response.status_code).is_equal_to(409)


def test_wrong_password_prevents_login(http_client: TestClient) -> None:
    SUT = http_client
    SUT.post("/auth/register", json={
        "email": "carol@example.com",
        "password": "correct-password",
        "first_name": "Carol",
        "last_name": "White",
    })

    response = SUT.post("/auth/login", json={
        "email": "carol@example.com",
        "password": "wrong-password",
    })

    assert_that(response.status_code).is_equal_to(401)


def test_unauthenticated_request_to_protected_endpoint_is_rejected(http_client: TestClient) -> None:
    SUT = http_client

    response = SUT.get("/me")

    assert_that(response.status_code).is_equal_to(401)
