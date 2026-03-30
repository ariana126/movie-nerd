import os

import pytest
from alembic import command
from alembic.config import Config
from ddd import Identity
from pydm import ServiceContainer
from pathlib import Path

from movie_nerd.infrastructure.bootstrap.app import App
from movie_nerd.infrastructure.persistence.sql_alchemy.connection import Connection
from movie_nerd.infrastructure.persistence.sql_alchemy.orm import Base
from movie_nerd.domain import User
from movie_nerd.domain.service import UserRepository


# Integration tests should use a dedicated DB.
os.environ["DB_DATABASE"] = os.environ.get("DB_TEST_DATABASE", "testdb")

PROJECT_ROOT = Path(__file__).resolve().parents[2]


App.boot()
service_container = ServiceContainer.get_instance()
connection: Connection = service_container.get_service(Connection)


@pytest.fixture(scope="session", autouse=True)
def _apply_migrations() -> None:
    # Run Alembic migrations via the Python API (no shell commands).
    alembic_cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="function", autouse=True)
def _clear_database() -> None:
    # Use explicit order + CASCADE to keep FK constraints happy.
    session = connection.get_session()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()


@pytest.fixture(scope="function")
def seeded_user() -> User:
    user = User(
        Identity.new(),
        "seeded-user@example.com",
        "seeded-password-hash",
        "SeedFirst",
        "SeedLast",
    )
    service_container.get_service(UserRepository).save(user)
    return user
