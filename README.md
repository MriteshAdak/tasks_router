# tasks_router

Minimal FastAPI project scaffold with SQLAlchemy (async) for Postgres.

Getting started:

1. Using Poetry (recommended):

```bash
# install poetry if needed
curl -sSL https://install.python-poetry.org | python3 -
poetry install
poetry run uvicorn app.main:app --reload
```

To generate a `requirements.txt` for containers or CI:

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

2. Copy `.env.example` to `.env` and set `DATABASE_URL`.
