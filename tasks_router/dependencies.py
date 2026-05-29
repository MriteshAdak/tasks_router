from typing import Generator

import structlog
from fastapi import Depends
from sqlalchemy.orm import Session

from tasks_router.repositories.task_repo import TaskRepository
from tasks_router.repositories.user_repo import UserRepository
from tasks_router.services.task_service import TaskServices
from tasks_router.services.user_service import UserService
from tasks_router.infrastructure.initiate_db import Database
from tasks_router.infrastructure.configurations import settings

db: Database = Database(settings)
logger = structlog.get_logger(__name__)

def get_db() -> Generator[Session, None, None]:
    """Dependency function to provide a database session."""
    logger.debug("db.session.open")
    try:
        yield from db.get_db()
    finally:
        logger.debug("db.session.close")

def get_task_repository(db: Session = Depends(get_db)) -> TaskRepository:
    """Dependency function to provide a TaskRepository instance."""
    logger.debug("dependencies.task_repository")
    return TaskRepository(db)

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Dependency function to provide a UserRepository instance."""
    logger.debug("dependencies.user_repository")
    return UserRepository(db)

def get_task_services(task_repo: TaskRepository = Depends(get_task_repository)) -> TaskServices:
    """Dependency function to provide a TaskServices instance."""
    logger.debug("dependencies.task_service")
    return TaskServices(task_repo)

def get_user_services(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    """Dependency function to provide a UserService instance."""
    logger.debug("dependencies.user_service")
    return UserService(user_repo)
