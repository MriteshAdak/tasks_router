from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from tasks_router.repositories.task_repo import TaskRepository
from tasks_router.repositories.user_repo import UserRepository
from tasks_router.services.task_service import TaskServices
from tasks_router.services.user_service import UserService
from tasks_router.database.initiate_db import Database
from tasks_router.database.config_db import settings

db: Database = Database(settings)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for request handlers.

    Yields:
        Active SQLAlchemy session bound to configured engine.
    """
    yield from db.get_db()


def get_task_repository(db: Session = Depends(get_db)) -> TaskRepository:
    """Build a task repository from a request-scoped session.

    Args:
        db: Request-scoped SQLAlchemy session.

    Returns:
        Repository used by task services.
    """
    return TaskRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Build a user repository from a request-scoped session.

    Args:
        db: Request-scoped SQLAlchemy session.

    Returns:
        Repository used by user services.
    """
    return UserRepository(db)


def get_task_services(task_repo: TaskRepository = Depends(get_task_repository)) -> TaskServices:
    """Build task service with injected repository.

    Args:
        task_repo: Repository dependency for task persistence.

    Returns:
        Service object used by task routes.
    """
    return TaskServices(task_repo)


def get_user_services(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    """Build user service with injected repository.

    Args:
        user_repo: Repository dependency for user persistence.

    Returns:
        Service object used by user routes.
    """
    return UserService(user_repo)
