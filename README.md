# FastAPI Project Structure Best Practices: Routers, Models, Controllers & Alembic Migrations

[![Python 3.14](https://img.shields.io/badge/python-3.14-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLModel](https://img.shields.io/badge/SQLModel-async%20MySQL-4479A1?logo=mysql&logoColor=white)](https://sqlmodel.tiangolo.com/)
[![Alembic](https://img.shields.io/badge/Alembic-migrations-6BA81E)](https://alembic.sqlalchemy.org/)
[![Redis](https://img.shields.io/badge/Redis-JWT%20blacklist-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![uv](https://img.shields.io/badge/uv-package%20manager-DE5FE9)](https://docs.astral.sh/uv/)

A production-style **FastAPI project structure** example using **SQLModel**, **async MySQL**, **Alembic database migrations**, **JWT authentication** with **Redis token blacklisting**, and a clean **router → controller → model** layered architecture. Use it as a reference for how to organize folders in a scalable FastAPI application.

**Keywords:** FastAPI best practices, FastAPI folder structure, FastAPI Alembic migrations, SQLModel async MySQL, FastAPI JWT auth, FastAPI dependency injection, FastAPI OAuth2PasswordBearer, Scalar API docs.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [FastAPI Folder Structure](#fastapi-folder-structure)
- [Layered Architecture: How a Request Flows](#layered-architecture-how-a-request-flows)
- [FastAPI Best Practices Used in This Project](#fastapi-best-practices-used-in-this-project)
- [Alembic Migrations Best Practices](#alembic-migrations-best-practices)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [API Documentation (Swagger, ReDoc, Scalar)](#api-documentation-swagger-redoc-scalar)
- [Common Pitfall: Multiple OAuth2PasswordBearer Schemes](#common-pitfall-multiple-oauth2passwordbearer-schemes)
- [FAQ](#faq)

---

## Features

- Modular **FastAPI routers** per domain (`auth`, `shipment`, `partner`)
- **Controller (service) layer** with a reusable `BaseController` for CRUD
- **SQLModel** table models with relationships and an async **MySQL** engine (`asyncmy`)
- **Alembic** async migrations with autogenerate support
- **JWT authentication** for two user types (users and delivery partners)
- **Logout via Redis token blacklist** using the JWT `jti` claim and automatic TTL
- Password hashing with **Argon2** (`pwdlib`)
- Typed configuration with **pydantic-settings** and `.env` files
- Reusable **`Annotated` dependencies** for DB sessions, controllers and the current user
- Interactive API docs with **Swagger UI**, **ReDoc** and **Scalar**

## Tech Stack

| Layer            | Library                                  |
| ---------------- | ---------------------------------------- |
| Web framework    | FastAPI, Uvicorn                         |
| ORM / models     | SQLModel (SQLAlchemy 2.x + Pydantic v2)  |
| Database         | MySQL via `asyncmy` (async driver)       |
| Migrations       | Alembic (async `env.py`)                 |
| Auth             | PyJWT, OAuth2PasswordBearer, pwdlib[argon2] |
| Cache / blacklist| Redis (`redis[hiredis]`)                 |
| Settings         | pydantic-settings                        |
| API docs         | Swagger UI, ReDoc, scalar-fastapi        |
| Package manager  | uv (Python 3.14)                         |

---

## FastAPI Folder Structure

```text
.
├── main.py                  # App entry point: creates FastAPI app, includes routers, lifespan
├── alembic.ini              # Alembic configuration (script_location = migrations)
├── pyproject.toml           # Dependencies (managed by uv)
├── .env.example             # Template for required environment variables
│
├── config/                  # App-wide infrastructure
│   ├── settings.py          # Typed settings loaded from .env (pydantic-settings)
│   ├── db.py                # Async engine, session dependency (DBSession)
│   ├── redis.py             # Redis client + JWT blacklist helpers
│   └── security.py          # Password hashing, JWT encode/decode, auth dependencies
│
├── models/                  # SQLModel database tables (table=True)
│   ├── auth_model.py        # UserModel        -> users
│   ├── partner_model.py     # PartnerModel     -> delivery_partners
│   └── shipment_model.py    # ShipmentModel    -> shipment
│
├── schema/                  # Pydantic request/response schemas (API contracts)
│   ├── auth_schema.py
│   ├── partner_schema.py
│   └── shipment_schema.py
│
├── controllers/             # Business logic (service layer)
│   ├── base_controller.py   # Generic _get / _add / _get_by / _get_all helpers
│   ├── auth_controller.py
│   ├── partner_controller.py
│   └── shipment_controller.py
│
├── deps/                    # FastAPI dependency providers (Annotated + Depends)
│   ├── auth_dep.py
│   ├── partner_dep.py
│   └── shipment_dep.py
│
├── routers/                 # HTTP layer: APIRouter per domain
│   ├── auth_router.py       # /auth/*
│   ├── partner_router.py    # /partner/*
│   └── shipment_router.py   # /shipment/*
│
└── migrations/              # Alembic migration environment
    ├── env.py               # Async migration runner, imports all models
    └── versions/            # One file per schema change
        ├── 26451b8f47a0_init.py
        └── df9b2a726f15_partner_table.py
```

### What belongs in each folder

| Folder         | Responsibility | Should **not** contain |
| -------------- | -------------- | ---------------------- |
| `routers/`     | HTTP concerns: path, method, status code, `response_model`, tags | SQL queries or business rules |
| `controllers/` | Business logic, DB reads/writes through the session | `Request`/`Response` objects or routing |
| `models/`      | Database tables and relationships (`table=True`) | API-only fields like `password_confirm` |
| `schema/`      | Request bodies and response shapes | DB sessions or queries |
| `deps/`        | Wiring: build controllers from a `DBSession` | Business logic |
| `config/`      | Settings, DB engine, Redis, security helpers | Domain-specific logic |
| `migrations/`  | Versioned database schema changes | Seed data mixed with schema changes |

---

## Layered Architecture: How a Request Flows

```text
HTTP request
   │
   ▼
routers/shipment_router.py      @router.post("/shipment/create")
   │  validates body with schema/ShipmentCreate
   │  injects GetUserFromToken  (config/security.py)
   │  injects ShipmentControllerDep (deps/shipment_dep.py)
   ▼
controllers/shipment_controller.py   ShipmentController.create()
   │  uses BaseController._add()
   ▼
models/shipment_model.py        ShipmentModel  ──►  MySQL (async session)
   │
   ▼
schema/ShipmentResponse         filtered response returned to the client
```

Each layer only talks to the layer below it. This keeps routes thin, business logic testable, and database code in one place.

---

## FastAPI Best Practices Used in This Project

1. **One router per domain** with `APIRouter(prefix=..., tags=[...])`, included in `main.py`. Tags group endpoints in the docs.
2. **Separate DB models from API schemas.** `models/` defines tables; `schema/` defines what clients send and receive. Always set `response_model` so internal fields (like password hashes) never leak.
3. **Reusable `Annotated` dependencies.** Declare once, reuse everywhere:
   ```python
   DBSession = Annotated[AsyncSession, Depends(get_session)]
   GetUserFromToken = Annotated[UserTokenData, Depends(verify_user_with_token)]
   ShipmentControllerDep = Annotated[ShipmentController, Depends(init_shipment_controller)]
   ```
4. **Controller / service layer.** Routes call controllers; controllers own queries. A shared `BaseController` removes repeated CRUD code.
5. **Async all the way.** Async engine (`create_async_engine`), `AsyncSession`, async Redis and async Alembic migrations.
6. **Typed, validated settings.** `pydantic-settings` loads `.env`, fails fast if a variable is missing, and builds the DB URL with `quote_plus` so special characters in passwords are safe.
7. **Secure authentication.**
   - Argon2 password hashing (`PasswordHash.recommended()`).
   - JWTs carry `exp` and a unique `jti`.
   - Logout stores the `jti` in Redis with a TTL equal to the token's remaining lifetime, so the blacklist cleans itself up.
8. **Consistent file naming.** `<domain>_router.py`, `<domain>_controller.py`, `<domain>_model.py`, `<domain>_schema.py`, `<domain>_dep.py` make features easy to locate.
9. **Secrets stay out of git.** Commit `.env.example`, never `.env`.

### Adding a new feature (checklist)

1. `models/<domain>_model.py` – define the SQLModel table.
2. Import the model in `migrations/env.py` so Alembic autogenerate can see it.
3. `schema/<domain>_schema.py` – request and response schemas.
4. `controllers/<domain>_controller.py` – extend `BaseController`.
5. `deps/<domain>_dep.py` – expose an `Annotated` controller dependency.
6. `routers/<domain>_router.py` – add endpoints and include the router in `main.py`.
7. Generate and apply a migration (see below).

---

## Alembic Migrations Best Practices

This project uses an **async Alembic environment** (`migrations/env.py`) that:

- reads the DB URL from `config.settings` instead of hard-coding it in `alembic.ini`
  (`%` is escaped as `%%` for configparser),
- sets `target_metadata = SQLModel.metadata` for **autogenerate**,
- imports every model (`UserModel`, `PartnerModel`, `ShipmentModel`) so their tables are registered.

### Common Alembic commands

```bash
# Create a new migration from model changes
uv run alembic revision --autogenerate -m "add shipment table"

# Apply all pending migrations
uv run alembic upgrade head

# Roll back the last migration
uv run alembic downgrade -1

# Show current revision and history
uv run alembic current
uv run alembic history --verbose
```

### Migration rules of thumb

- **Every schema change is a migration.** Never edit tables by hand in production.
- **Always review autogenerated files** before committing. Autogenerate can miss renames, enum changes and server defaults.
- **Use short, descriptive messages** (`-m "add partner_id to shipment"`); the message becomes part of the file name.
- **Never edit a migration that has already been applied** in a shared environment. Create a new one instead.
- **Keep `upgrade()` and `downgrade()` symmetric** so rollbacks work.
- **Import new models in `migrations/env.py`**, or autogenerate will not detect them.
- **Prefer Alembic over `create_all` in production.** `main.py` currently calls `SQLModel.metadata.create_all` on startup, which is handy while learning, but it can create tables Alembic does not know about. In production, rely on `alembic upgrade head` only.
- **SQLModel string columns:** autogenerated files may reference `sqlmodel.sql.sqltypes.AutoString`. Make sure `import sqlmodel` is present in the migration (or in `script.py.mako`).

---

## Getting Started

### Prerequisites

- Python **3.14+**
- [uv](https://docs.astral.sh/uv/)
- MySQL server
- Redis server

### Installation

```bash
# 1. Install dependencies
uv sync

# 2. Configure environment
cp .env.example .env      # then fill in your values

# 3. Run database migrations
uv run alembic upgrade head

# 4. Start the development server
uv run uvicorn main:app --reload
```

The API runs at `http://localhost:8000`.

---

## Environment Variables

Defined in `config/settings.py` and loaded from `.env`:

| Variable      | Description                        | Example       |
| ------------- | ---------------------------------- | ------------- |
| `DB_HOST`     | MySQL host                         | `localhost`   |
| `DB_PORT`     | MySQL port                         | `3306`        |
| `DB_USER`     | MySQL user                         | `root`        |
| `DB_PASSWORD` | MySQL password                     | `secret`      |
| `DB_NAME`     | Database name                      | `shipments`   |
| `JWT_SECRET`  | Secret key used to sign JWTs       | long random string |
| `JWT_ALGO`    | JWT signing algorithm              | `HS256`       |
| `REDIS_HOST`  | Redis host                         | `localhost`   |
| `REDIS_PORT`  | Redis port                         | `6379`        |

---

## API Endpoints

### Auth (`/auth`) – users

| Method | Path           | Auth | Description |
| ------ | -------------- | ---- | ----------- |
| POST   | `/auth/create` | –    | Register a user, returns a token |
| POST   | `/auth/login`  | –    | Log in with JSON body |
| POST   | `/auth/token`  | –    | OAuth2 password form login (used by docs "Authorize") |
| GET    | `/auth/me`     | User | Current user profile |
| GET    | `/auth/logout` | User | Blacklist the current token |

### Partner (`/partner`) – delivery partners

| Method | Path              | Auth    | Description |
| ------ | ----------------- | ------- | ----------- |
| POST   | `/partner/create` | –       | Register a delivery partner |
| POST   | `/partner/login`  | –       | Log in with JSON body |
| POST   | `/partner/token`  | –       | OAuth2 password form login |
| GET    | `/partner/me`     | Partner | Current partner profile |
| GET    | `/partner/logout` | Partner | Blacklist the current token |

### Shipment (`/shipment`)

| Method | Path               | Auth | Description |
| ------ | ------------------ | ---- | ----------- |
| POST   | `/shipment/create` | User | Create a shipment for the logged-in user |
| GET    | `/shipment/`       | User | List the logged-in user's shipments |

Shipment status values: `placed`, `in_transit`, `out_of_delivery`, `delivered`.

---

## API Documentation (Swagger, ReDoc, Scalar)

| UI         | URL                                  |
| ---------- | ------------------------------------ |
| Swagger UI | http://localhost:8000/docs           |
| ReDoc      | http://localhost:8000/redoc          |
| Scalar     | http://localhost:8000/scalar         |
| OpenAPI    | http://localhost:8000/openapi.json   |

---

## Common Pitfall: Multiple OAuth2PasswordBearer Schemes

When an app has more than one `OAuth2PasswordBearer` (here: users at `/auth/token` and partners at `/partner/token`), each one **must have a unique `scheme_name`**.

Without it, both default to the class name `"OAuth2PasswordBearer"`. FastAPI stores security schemes in the OpenAPI spec by name, so the scheme from the **last registered router** overwrites the others. In this project `partner_router` is included last, so Swagger and Scalar show `/partner/token` even for user routes like `/shipment/create`.

This only affects the docs. At runtime each route still validates the token with its own dependency.

```python
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", scheme_name="UserAuth")
partner_oauth_scheme = OAuth2PasswordBearer(tokenUrl="/partner/token", scheme_name="PartnerAuth")
```

---

## FAQ

### What is the best folder structure for a FastAPI project?
Split code by responsibility: `routers/` (HTTP), `controllers/` (business logic), `models/` (database tables), `schema/` (request/response), `deps/` (dependency wiring), `config/` (settings, DB, security) and `migrations/` (Alembic). Within each folder, use one file per domain.

### Should I use `SQLModel.metadata.create_all` or Alembic?
Use `create_all` only for quick prototypes. Use **Alembic migrations** for any shared or production database, so every schema change is versioned, reviewable and reversible.

### Why doesn't Alembic autogenerate detect my new table?
The model is not imported in `migrations/env.py`, so it is not registered on `SQLModel.metadata`. Import it there.

### How does logout work with stateless JWTs?
Each token has a unique `jti`. On logout, the `jti` is stored in Redis with a TTL equal to the token's remaining lifetime. Every protected request checks Redis and rejects blacklisted tokens.

### Why are models and schemas separate?
Database models describe storage; schemas describe the public API. Keeping them separate prevents leaking sensitive fields and lets the API and the database evolve independently.
