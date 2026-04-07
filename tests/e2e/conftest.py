from __future__ import annotations

import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from pydm import ServiceContainer

from movie_nerd.application.auth.auth_service import AuthService
from movie_nerd.infrastructure.auth import HmacTokenService, Pbkdf2PasswordHasher, SQLAlchemyUserStore
from movie_nerd.infrastructure.bootstrap.app import App
from movie_nerd.infrastructure.http.app_factory import create_app
from movie_nerd.infrastructure.persistence.sql_alchemy.connection import Connection
from movie_nerd.infrastructure.persistence.sql_alchemy.orm import Base

os.environ["DB_DATABASE"] = os.environ.get("DB_TEST_DATABASE", "testdb")

PROJECT_ROOT = Path(__file__).resolve().parents[2]

App.boot()
_container = ServiceContainer.get_instance()
_connection: Connection = _container.get_service(Connection)

try:
    with _connection.engine.connect() as _conn:
        _conn.exec_driver_sql("SELECT 1")
except Exception as exc:  # noqa: BLE001
    pytest.skip(f"Integration DB not available: {exc}", allow_module_level=True)


@pytest.fixture(scope="session", autouse=True)
def _apply_migrations() -> None:
    alembic_cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="function", autouse=True)
def _clear_database() -> None:
    session = _connection.get_session()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()


@pytest.fixture(scope="session")
def http_client() -> TestClient:
    user_store = SQLAlchemyUserStore(connection=_connection)
    password_hasher = Pbkdf2PasswordHasher(iterations=1_000)
    token_service = HmacTokenService(secret="e2e-test-secret", expires_in_seconds=60)
    auth_service = AuthService(
        user_store=user_store,
        password_hasher=password_hasher,
        token_service=token_service,
    )
    app = create_app(auth_service=auth_service)
    return TestClient(app)
