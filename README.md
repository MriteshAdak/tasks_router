# Updates
**Bugs Resolved**
1. User Creation  
*Issue*: User creation flow required id field to be passed in the payload.  
*Resolution*: Created a new UserCreate schema without id parameter.

2. Auth Placeholder  
*Issue*: The get_current_user_id() called get_user_repository() directly without resolving the dependency.  
*Resolution*: Fixed the method signature to resolve the dependency before using it to get users.

3. Logging Config (identified by Claude)  
   *Issues*:
      1. Incorrect exception_processor assignment.
      2. configure_logging._configured guard is not thread-safe.
      3. root_logger.handlers = [handler] are replaced without calling .close() on them first.
      4. bind_contextvars_middleware — Context Not Cleared on Exception Path.  

   *Resolutions*:
      1. using ExceptionRenderer() instead.
      2. using a threading.Lock to make the idempotency guard thread-safe.
      3. using a threading.Lock to make the idempotency guard thread-safe.
      4. using try/finally for contextvars.

**Additions**
1. Added docker compose to orchestrate db and backend services for dev testing.

**Pending**
1. Tests have not yet been completely vetted.
2. User Input validations needs to be tightended.
3. Logging coverage is not yet comprehensive.
4. Auth not yet implemented.
5. Docstrings are not yet in place.

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
- **Dockerized**: Includes a functional Dockerfile relying on a Python 3.12-slim base and a docker-compose.yaml for local deployment.

## Getting Started

### Prerequisites
- Docker Engine
- Python3-pip
- Git clone of the repository

### Quickstart (Local Deployment)
1. **Configure Environment Variables**  
   Create a `.env` file referencing the Database Settings configured in `infrastructure/configurations.py`. Use .env.example for reference. Skip the SSL mode and SSL Root Cert for local deployment:
   ```dotenv
   # Example .env configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_USERNAME=postgres
   DB_PASSWORD=test123
   DB_DATABASE=postgres
   ```

2. **Install dependencies locally**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Start the DB container/service**  
   Run docker:
   ```bash
   docker compose up db
   ```

4. **Run Alembic Upgrade**
   ```bash
   alembic upgrade head
   ```

5. **Start the backend container/service**
   ```bash
   docker compose up backend
   ```

6. **Run the application**  
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
