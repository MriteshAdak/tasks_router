from contextlib import asynccontextmanager

from fastapi import FastAPI

from tasks_router.routers.task_router import router as task_router
from tasks_router.routers.user_router import router as user_router
from tasks_router.routers.system_router import router as system_router
from tasks_router.database.initiate_db import Base
from tasks_router.dependencies import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan function to handle application startup and shutdown events. It creates the database tables on startup."""
    engine = db.get_engine()
    Base.metadata.create_all(engine)
    yield
    engine.dispose()

app = FastAPI(
    title="Tasks Router API",
    description="API for managing tasks and users with PostgreSQL database integration.",
    version="1.0.0",
    redirect_slashes=False,
    lifespan=lifespan
)

app.include_router(task_router)
app.include_router(user_router)
app.include_router(system_router)