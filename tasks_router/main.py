import structlog
from fastapi import FastAPI
from asgi_correlation_id import CorrelationIdMiddleware

from tasks_router.logging_config import (
    CORRELATION_ID_HEADER,
    structlog_bind_middleware,
    configure_logging,
)
from tasks_router.routers.task_router import router as task_router
from tasks_router.routers.user_router import router as user_router
from tasks_router.routers.system_router import router as system_router
from tasks_router.middleware.cors import register_cors_middleware

configure_logging()
logger = structlog.get_logger(__name__)

app = FastAPI(
    title="Tasks Router API",
    description="API for managing tasks and users with PostgreSQL database integration.",
    version="1.0.0",
)

register_cors_middleware(app)


@app.middleware("http")
async def structlog_context_middleware(request, call_next):
    return await structlog_bind_middleware(request, call_next)


app.add_middleware(
    CorrelationIdMiddleware,
    header_name=CORRELATION_ID_HEADER,
    update_request_header=True,
)

app.include_router(task_router)
app.include_router(user_router)
app.include_router(system_router)
