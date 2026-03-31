# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Environment setup

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e "[dev]"
```

Configuration is via `.env` (see `README.md` for required variables). Postgres is required for most functionality.

### Run the API

```bash
./scripts/run_http_server.sh --reload
```

Defaults to `HOST=0.0.0.0`, `PORT=8000`. Override via environment variables.

Health check:

```bash
curl http://localhost:8000/health
```

### Database migrations

```bash
alembic upgrade head
```

Or via helper script:

```bash
./scripts/migration.sh upgrade-latest
./scripts/migration.sh rollback-latest
./scripts/migration.sh create "message"
```

### Tests

Run all unit tests:

```bash
pytest -q
```

Run a single test file:

```bash
pytest tests/unit/application/use_case/test_send_message.py
```

Run integration tests (requires Postgres):

```bash
DB_TEST_DATABASE=testdb pytest -q tests/integration
```

If the test database is unreachable, integration tests are skipped.

## High-Level Architecture

This is a **DDD-style backend** with explicit separation between domain, application, and infrastructure layers.

### Layers

- **Domain (`src/movie_nerd/domain/`)**
  - Pure business concepts: domain events, service interfaces, and core rules.
  - No framework or database dependencies.
  - Example: chat-related events and repository interfaces.

- **Application (`src/movie_nerd/application/`)**
  - Use cases that orchestrate domain logic.
  - Thin, explicit classes/functions such as `start_chat` and `send_message`.
  - Depends on domain abstractions, not concrete infrastructure.

- **Infrastructure (`src/movie_nerd/infrastructure/`)**
  - Adapters and implementations:
    - `http/`: FastAPI endpoints and middleware
    - `persistence/`: SQLAlchemy mappings and repositories
    - `bootstrap/`: application wiring (dependency injection, startup)
  - This is the only layer allowed to depend on frameworks and external systems.

### Dependency Direction

```
Domain <- Application <- Infrastructure
```

Dependencies always point inward. Domain is framework-agnostic.

### Repositories

- Repository interfaces live in the domain layer.
- SQLAlchemy-backed implementations live under:
  `infrastructure/persistence/sql_alchemy/repositories/`.
- Tests often use explicit test doubles instead of the real database.

### HTTP API

- FastAPI is used as a thin transport layer.
- Request handling delegates quickly to application use cases.
- Authentication is token-based (email/password → signed token) with middleware enforcing auth.

### Testing Strategy

- **Unit tests**: exercise domain and application logic without infrastructure.
- **Integration tests**: run against Postgres, applying migrations in code.
- Test doubles for repositories live under `tests/test_double/`.

## Notes for Future Changes

- Keep domain code free of FastAPI, SQLAlchemy, and environment access.
- New features typically require:
  1. A new application use case
  2. Domain additions (events or interfaces) if needed
  3. Infrastructure wiring (HTTP + persistence)
- Favor adding new files over growing existing ones to preserve layer clarity.