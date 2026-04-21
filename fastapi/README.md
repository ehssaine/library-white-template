# FastAPI Production Architecture

A reference layout for a production-grade FastAPI service. The goal is a clear
separation of concerns so each layer has exactly one reason to change.

## Layer responsibilities

```
HTTP request
     │
     ▼
┌──────────────┐   Pydantic validation, auth, HTTP status codes.
│ api/ routers │   No business logic. Delegates to services.
└──────┬───────┘
       ▼
┌──────────────┐   Business rules, cross-entity orchestration,
│ services/    │   transactions, domain errors.
└──────┬───────┘
       ▼
┌──────────────┐   Pure persistence: CRUD, queries, joins.
│ dao/         │   No HTTP, no business rules. One class per aggregate.
└──────┬───────┘
       ▼
┌──────────────┐   SQLAlchemy ORM entities (table mappings).
│ models/      │   Never returned over the wire directly.
└──────┬───────┘
       ▼
┌──────────────┐   AsyncEngine, AsyncSession factory,
│ db/          │   lifecycle, connection pool, migrations entry.
└──────────────┘
```

## Folder map

```
fastapi/
├── app/
│   ├── main.py                  # App factory, lifespan, router/middleware wiring
│   │
│   ├── core/                    # Cross-cutting infrastructure (framework-agnostic)
│   │   ├── config.py            # Pydantic-settings, env-driven configuration
│   │   ├── logging.py           # structlog bootstrap with request-id binding
│   │   ├── security.py          # Password hashing (argon2), JWT encode/decode
│   │   └── exceptions.py        # Domain exceptions + FastAPI exception handlers
│   │
│   ├── db/                      # Database connection & session management
│   │   ├── base.py              # Declarative Base; imports models for Alembic
│   │   ├── session.py           # Async engine, sessionmaker, get_db() dependency
│   │   └── init_db.py           # Bootstrap data (first superuser, reference data)
│   │
│   ├── models/                  # SQLAlchemy ORM models (DB schema)
│   │   ├── base.py              # TimestampMixin, UUID PK mixin
│   │   └── user.py
│   │
│   ├── schemas/                 # Pydantic DTOs (wire format, validation)
│   │   ├── user.py              # UserCreate / UserRead / UserUpdate
│   │   └── token.py
│   │
│   ├── dao/                     # Data Access Objects — pure persistence
│   │   ├── base.py              # Generic CRUDBase[Model, Create, Update]
│   │   └── user.py
│   │
│   ├── services/                # Business logic layer
│   │   ├── user_service.py
│   │   └── auth_service.py
│   │
│   ├── api/                     # HTTP layer
│   │   ├── deps.py              # get_db, get_current_user, require_roles
│   │   └── v1/
│   │       ├── router.py        # Aggregates v1 endpoints
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── users.py
│   │           └── health.py
│   │
│   └── middleware/
│       └── request_id.py        # Correlation ID for logs + response headers
│
├── alembic/                     # DB migrations
├── tests/                       # unit/ and integration/
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
└── .env.example
```

## Why DAO *and* service?

- **DAO** answers "how do I read/write this aggregate?". It knows SQLAlchemy,
  indexes, filter predicates. It does not know about passwords, JWTs, or emails.
- **Service** answers "what does the business do?". It composes DAOs, enforces
  invariants, emits events, and owns the unit-of-work (commit/rollback).

This split lets you swap the persistence backend (e.g. move a read path to a
read replica, cache, or search index) without touching business logic — and
lets you unit-test services with a fake DAO.

## Why async SQLAlchemy 2.0?

FastAPI is async-first. Using `AsyncSession` + `asyncpg` avoids thread-pool
saturation under load. The `Mapped[...]` + `mapped_column` style gives typed
models that play well with mypy.

## Running locally

```bash
cp .env.example .env
docker compose up -d db
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

OpenAPI docs: <http://localhost:8000/docs>
