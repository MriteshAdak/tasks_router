# Tasks Router

A FastAPI service implementing a layered architecture pattern for managing tasks and users with PostgreSQL.

NOTE: branch "aws" has the serverless version of this code deployed as a Lambda Function connected to an Aurora DB.

This repository provides a clean, well-structured, and opinionated foundation for building scalable REST APIs equipped with synchronous database access (SQLAlchemy + psycopg2), database migrations (Alembic), structured logging, and dependency management via PDM.

## Key Features
- **FastAPI Framework**: Modern, fast web framework for building APIs.
- **SQLAlchemy ORM**: Synchronous database interactions, configured for PostgreSQL (`psycopg2-binary`).
- **Alembic Migrations**: Out-of-the-box support for managing schema iterations (`alembic.ini`, `migrations/`).
- **Layered Components Pattern**: Distinct boundaries across Routers, Services, Repositories, Schemas, and Models.
- **Structured Logging**: Deeply integrated `structlog` paired with `asgi-correlation-id` for structured context and request tracking.
- **Serverless Support**: Pre-configured with `mangum` and `boto3` capabilities, preparing the API for AWS Lambda deployment.
- **Dependency Management**: Powered by `PDM` via `pyproject.toml`.
- **Dockerized**: Includes a functional Dockerfile relying on a Python 3.12-slim base and a docker-compose.yaml for local deployment.

## Getting Started

### Prerequisites
- Docker Engine

### Quickstart (Local Deployment)
1. **Run Docker**
   ```bash
   docker compose up
   ```

2. **Run the application**  
   The application will be available at /localhost:8000. Access it from a browser. 
   Navigate to /docs to get to the Swagger UI for running the APIs.

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
├── utils.py                    # Utility funcitons for object transformation
├── auth_placeholder.py         # Auth placeholder for future auth implementation
└── dependencies.py             # Route injectors for DB sessions & logic
```

At the project root, you will additionally find the Alembic migration environments (`alembic/` and `alembic.ini`), PDM settings (`pyproject.toml`), a generic container definition (`dockerfile`), and the `tests/` directory.

**Pending**
1. User Input validations needs to be tightended.
2. Logging coverage is not yet comprehensive.
3. Auth not yet implemented.
4. Docstrings are not yet in place.
