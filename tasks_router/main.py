from contextlib import asynccontextmanager
# from mangum import Mangum
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
from tasks_router.models.base_model import Base
from tasks_router.dependencies import db

configure_logging()
logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan function to handle application startup and shutdown events. It creates the database tables on startup."""
    engine = db.get_engine()
    logger.info("app.startup")
    Base.metadata.create_all(engine)
    yield
    logger.info("app.shutdown")
    engine.dispose()

app = FastAPI(
    title="Tasks Router API",
    description="API for managing tasks and users with PostgreSQL database integration.",
    version="1.0.0",
    redirect_slashes=False,
    lifespan=lifespan
)


@app.middleware("http")
async def structlog_context_middleware(request, call_next):
    return await bind_contextvars_middleware(request, call_next)


app.add_middleware(
    CorrelationIdMiddleware,
    header_name=CORRELATION_ID_HEADER,
    update_request_header=True,
)

# handler = Mangum(app)

app.include_router(task_router)
app.include_router(user_router)
app.include_router(system_router)