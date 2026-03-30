# Movie Nerd

Minimal DDD-style backend with:

- **FastAPI** HTTP server
- **SQLAlchemy** ORM mappings on domain entities
- **Alembic** migrations
- Minimal **email/password auth** with a signed token and authentication middleware

## Requirements

- Python **3.10+**
- Postgres

## Setup

Create a virtualenv and install dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Example `.env`:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=mydb
DB_USERNAME=local
DB_PASSWORD=local

# Token signing secret (set this in real deployments)
AUTH_SECRET=change-me
```

## Run the API

```bash
./scripts/run_http_server.sh --reload
```

Defaults:

- `HOST=0.0.0.0`
- `PORT=8000`

Override:

```bash
HOST=127.0.0.1 PORT=8000 ./scripts/run_http_server.sh --reload
```

Health check:

```bash
curl -i "http://localhost:8000/health"
```

## Auth API

### Register

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "MyStrongPassword123",
    "first_name": "Ariana",
    "last_name": "Maghsoudi"
  }'
```

### Login (get token)

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "MyStrongPassword123"
  }'
```

Example response:

```json
{"token":"<TOKEN_HERE>"}
```

### Authenticated endpoint

```bash
curl -X GET "http://localhost:8000/me" \
  -H "Authorization: Bearer <TOKEN_HERE>"
```

## Migrations

Run migrations with Alembic directly:

```bash
alembic upgrade head
```

Or use the helper script:

```bash
./scripts/migration.sh upgrade-latest
./scripts/migration.sh rollback-latest
./scripts/migration.sh create "your message"
```

## Testing

### Unit tests

```bash
pytest -q
```

### Integration tests (Postgres required)

Integration tests run migrations in code and use a dedicated database name:

- `DB_TEST_DATABASE` if set
- otherwise `testdb`

Example:

```bash
DB_TEST_DATABASE=testdb pytest -q tests/integration
```

If the test database is not reachable, integration tests will be skipped.
You are responsible for creating the `testdb` database and ensuring the `.env` credentials can connect.
