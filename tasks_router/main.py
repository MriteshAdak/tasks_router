from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from asgi_correlation_id import CorrelationIdMiddleware

from tasks_router.logging_config import (
    CORRELATION_ID_HEADER,
    bind_contextvars_middleware,
    configure_logging,
)
from tasks_router.routers.task_router import router as task_router
from tasks_router.routers.user_router import router as user_router
from tasks_router.routers.system_router import router as system_router
from tasks_router.dependencies import db
from tasks_router.middleware.cors import register_cors_middleware

configure_logging()
logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan function to handle application startup and shutdown events. It creates the database tables on startup."""
    engine = db.get_engine()
    logger.info("app.startup")
    # To be replaced with Alembic migrations
    # Base.metadata.create_all(engine)
    yield
    logger.info("app.shutdown")
    engine.dispose()

app = FastAPI(
    title="Tasks Router API",
    description="API for managing tasks and users with PostgreSQL database integration.",
    version="1.0.0",
    lifespan=lifespan
)

register_cors_middleware(app)


@app.middleware("http")
async def structlog_context_middleware(request, call_next):
    return await bind_contextvars_middleware(request, call_next)


app.add_middleware(
    CorrelationIdMiddleware,
    header_name=CORRELATION_ID_HEADER,
    update_request_header=True,
)

app.include_router(task_router)
app.include_router(user_router)
app.include_router(system_router)