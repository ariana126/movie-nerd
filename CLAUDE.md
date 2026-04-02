# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # then fill in DB credentials and AUTH_SECRET
```

## Common Commands

### Run the server
```bash
./scripts/run_http_server.sh
```

### Run tests
```bash
# All unit tests (no DB needed)
pytest -q

# Single test file
pytest tests/unit/infrastructure/http/test_auth.py -q

# Single test by name
pytest tests/unit/application/use_case/test_start_chat.py::test_started_chat_is_saved -q

# Integration tests (requires Postgres)
DB_TEST_DATABASE=testdb pytest -q tests/integration
```

### Database migrations
```bash
./scripts/migration.sh  # wraps alembic commands
alembic upgrade head
alembic revision --autogenerate -m "description"
```

## Architecture

The project uses strict **Domain-Driven Design (DDD)** with three layers. Dependencies flow inward: Infrastructure → Application → Domain.

### Domain Layer (`src/movie_nerd/domain/`)
Pure business logic with zero framework dependencies. Key aggregates: `User` and `Chat` (which contains `ChatMessage` entities). Domain events (`ChatStarted`, `UserSentMessage`) are emitted via `_record_that()` from the `dddx` library and retrieved with `release_events()`. Repository interfaces (`UserRepository`, `ChatRepository`) are defined here as ABCs.

**Important**: Domain entities directly subclass SQLAlchemy's `Base` via a custom `DeclarativeABCMeta` metaclass that merges `DeclarativeMeta` + `ABCMeta`. This avoids a separate ORM mapping layer — ORM column definitions live on the domain objects themselves.

### Application Layer (`src/movie_nerd/application/`)
Orchestrates domain objects via use cases and services. Uses `typing.Protocol` interfaces (`UserStore`, `PasswordHasher`, `TokenService`) so `AuthService` is testable without infrastructure. Use cases follow a CQRS-style Command + Handler pattern (`StartChatCommandHandler`, `SendMessageCommandHandler`).

### Infrastructure Layer (`src/movie_nerd/infrastructure/`)
- **HTTP** (`infrastructure/http/`): FastAPI app wired in `app_factory.py`. Routes: `GET /health`, `POST /auth/register`, `POST /auth/login`, `GET /me`. `AuthenticationMiddleware` resolves Bearer tokens to `request.state.user` (invalid tokens yield unauthenticated state, not 401 — routes enforce auth themselves).
- **Auth** (`infrastructure/auth/`): `Pbkdf2PasswordHasher` (PBKDF2-HMAC-SHA256, 100k iterations). `HmacTokenService` uses a **custom signed token format** — NOT JWT: `base64url(JSON payload).base64url(HMAC-SHA256 sig)`, 1-hour expiry.
- **Persistence** (`infrastructure/persistence/sql_alchemy/`): `SQLAlchemyBaseRepository` opens a new session per operation (no Unit of Work). Custom `TypeDecorator`s for value objects (`IdentityType`, `EmailType`) in `orm.py`.
- **Bootstrap** (`infrastructure/bootstrap/app.py`): `App.boot()` loads `.env` and wires `pydm` (IoC container) binding repository interfaces to SQLAlchemy implementations.

### Testing Conventions
- **`assertpy`** is used for all assertions instead of bare `assert`.
- **Test doubles** in `tests/test_double/` use `SpyEntityRepository` from `dddx` for in-memory persistence with spy assertions.
- **Integration test isolation**: Alembic runs once per session; all table rows are deleted (reverse FK order) before each test function.
- Integration tests auto-skip if the test DB is unreachable.
