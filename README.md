(Some bugs identified. Work in progress)

# Tasks Router

A FastAPI service implementing a layered architecture pattern for managing tasks and users with PostgreSQL. 

This repository provides a clean, well-structured, and opinionated foundation for building scalable REST APIs equipped with synchronous database access (SQLAlchemy + psycopg2), database migrations (Alembic), structured logging, and dependency management via PDM.

## Key Features
- **FastAPI Framework**: Modern, fast web framework for building APIs.
- **SQLAlchemy ORM**: Synchronous database interactions, configured for PostgreSQL (`psycopg2-binary`).
- **Alembic Migrations**: Out-of-the-box support for managing schema iterations (`alembic.ini`, `migrations/`).
- **Layered Components Pattern**: Distinct boundaries across Routers, Services, Repositories, Schemas, and Models.
- **Structured Logging**: Deeply integrated `structlog` paired with `asgi-correlation-id` for structured context and request tracking.
- **Serverless Support**: Pre-configured with `mangum` and `boto3` capabilities, preparing the API for AWS Lambda deployment.
- **Dependency Management**: Powered by `PDM` via `pyproject.toml`.
- **Dockerized**: Includes a functional Dockerfile relying on a Python 3.12-slim base.

## Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL database
- PDM package manager

### Quickstart (Local Development)
1. **Clone and Setup**  
   Using PDM will optionally create a virtual environment and load dependencies inside it automatically:
   ```bash
   pdm install
   ```

2. **Configure Environment Variables**  
   Create a `.env` file referencing the Database Settings configured in `infrastructure/configurations.py` (using prefix `DB_`):
   ```dotenv
   # Example .env configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_USERNAME=user
   DB_PASSWORD=password
   DB_DATABASE=dbname
   
   # Or alternatively, you can pass a full connection URL:
   DB_URL=postgresql://user:password@localhost:5432/dbname
   ```

3. **Database Setup & Migrations**  
   First run migrations seamlessly:
   ```bash
   pdm run alembic upgrade head
   ```

4. **Run the Application**  
   Fire up the development server using PDM scripts:
   ```bash
   pdm run dev
   ```
   *Alternatively, standard uvicorn runs typically as: `uvicorn tasks_router.main:app --reload --host 0.0.0.0 --port 8000`*

## Project Structure Overview

```text
tasks_router/
├── main.py                     # FastAPI application factory and main entrypoint
├── routers/                    # API route definitions (system, task, user endpoints)
├── services/                   # Business logic encapsulating rules (task_service, user_service)
├── repositories/               # Database interactions handling CRUD (task_repo, user_repo)
├── models/                     # SQLAlchemy ORM definitions mapping tables
├── schema/                     # Pydantic models handling request/response validations
├── infrastructure/             # Database initialization and environment configurations
├── middleware/                 # Middleware extensions (e.g., CORS)
├── enums/                      # Constant enumerations (ssl modes, task statuses)
├── exceptions/                 # Custom error domains and logic
├── logging_config.py           # Structlog and correlation ID setup
└── dependencies.py             # Route injectors for DB sessions & logic
```

At the project root, you will additionally find the Alembic migration environments (`migrations/` and `alembic.ini`), PDM settings (`pyproject.toml`), a generic container definition (`dockerfile`), and the `tests/` directory ensuring system robustness.

## Working with Docker
To build and execute with Docker based on the generated requirements bundle:
```bash
docker build -t tasks-router .
docker run -p 8000:8000 --env-file .env tasks-router
```
*(ensure `requirements.txt.lock` is up to date ahead of builds via `pdm export`)*
