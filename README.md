# tasks_router

FastAPI service for task and user management with PostgreSQL persistence.

## Project structure

```text
tasks_router/
├── tasks_router/
│   ├── main.py                  # FastAPI app setup and router registration
│   ├── dependencies.py          # Dependency injection wiring
│   ├── auth_placeholder.py      # Temporary auth user-id provider
│   ├── routers/                 # API routes (tasks, users, system)
│   ├── services/                # Business logic layer
│   ├── repositories/            # Database access layer
│   ├── models/                  # SQLAlchemy models
│   ├── schema/                  # Request/response schemas
│   ├── database/                # DB settings and session management
│   ├── exceptions/              # Domain-specific exceptions
│   └── enums/                   # Shared enums
├── tests/                       # Test suite
├── migrations/                  # Alembic migration environment
├── alembic.ini                  # Alembic configuration
└── pyproject.toml               # Project metadata and dependencies
```

## Installation and local setup

### Prerequisites

- Python 3.12+
- PostgreSQL database

### 1) Clone and install

```bash
git clone https://github.com/MriteshAdak/tasks_router.git
cd tasks_router
python -m pip install -e .[dev]
```

### 2) Configure environment

Create a `.env` file from `.env.example` and provide valid database values.

```bash
cp .env.example .env
```

### 3) Run the API locally

```bash
uvicorn tasks_router.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### 4) Useful dev commands

```bash
ruff check .
pytest -q
```

## Deployment (AWS Lambda)

This project includes `mangum`, which is used to run FastAPI on AWS Lambda behind API Gateway.

1. Create a Lambda handler module (for example `tasks_router/lambda_handler.py`):

   ```python
   from mangum import Mangum
   from tasks_router.main import app

   handler = Mangum(app)
   ```

2. Package and deploy the app to AWS Lambda (zip-based or container-based deployment).
3. Set the Lambda handler to `tasks_router.lambda_handler.handler`.
4. Configure required environment variables in Lambda (matching `.env` keys).
5. Connect API Gateway (HTTP API or REST API) to the Lambda function.

After deployment, use the API Gateway URL to access the same endpoints (`/`, `/health`, `/tasks`, `/users`).
