# FastAPI Forge Boilerplate

Production-focused FastAPI foundation built for speed, maintainability, and real-world backend workloads.

## Why this project

This boilerplate is designed for teams that want a clean starting point with modern backend patterns already in place:

- Async-first API design with FastAPI and SQLAlchemy 2.0
- Modular domain layout under versioned routes
- Token-based auth flows, verification, and password reset scaffolding
- Redis + Celery integration for async/background workloads
- Alembic migration workflow
- Test suite structure with pytest and async support
- Security middleware and centralized exception handling

## Project layout

```text
.
├── main.py
├── api/
│   ├── core/                 # middlewares, exception handlers, shared base pieces
│   ├── database/             # async/sync database setup
│   ├── utils/                # config, dependencies, celery setup, helpers
│   └── v1/                   # feature modules (auth, user, payments, etc.)
├── migrations/               # alembic migration environment and versions
├── tests/                    # feature-oriented test suites
└── requirements.txt
```

## Quick start

1. Clone and enter the project.
2. Create and activate a virtual environment.
3. Install dependencies.
4. Copy environment variables.
5. Run migrations.
6. Start API and worker.

```bash
git clone <your-repo-url>
cd Boilerplate
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
alembic upgrade head
uvicorn main:app --reload --host 0.0.0.0 --port 7001
```

Run Celery worker in a second terminal:

```bash
celery -A api.utils.celery_setup.celery_app worker --loglevel=info
```

## Environment variables

Use .env.sample as source of truth. Configure at minimum:

- DATABASE_URL
- DATABASE_URL_SYNC
- JWT_SECRET
- JWT_ALGORITHM
- REDIS_URL
- CELERY_BROKER_URL
- CELERY_RESULT_BACKEND
- MAIL_USERNAME
- MAIL_PASSWORD
- MAIL_SERVER
- MAIL_PORT

## Testing

```bash
pytest -q
```

## What makes this boilerplate strong

- Clear separation of concerns per domain module
- Reusable service patterns
- Async database support with controlled session lifecycle
- Background task pipeline ready for production queues
- Centralized error handling and structured logging hooks

## Suggested roadmap

- Add Docker + docker-compose for one-command local startup
- Add CI pipeline for lint, tests, and migration checks
- Add OpenAPI examples for critical endpoints
- Add rate-limiting and idempotency keys for write-heavy endpoints
- Add observability (metrics + tracing) for production visibility

## License

MIT
