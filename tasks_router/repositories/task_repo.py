"""
Repository module for managing Task entities in the database.
This module defines the TaskRepository class, which provides methods for performing CRUD operations on Task entities using SQLAlchemy ORM.
"""

import uuid

import structlog
from sqlalchemy.orm import Session

from tasks_router.models.task_model import Task as TaskModel
from tasks_router.exceptions.custom_exceptions import TaskNotFoundException, DatabaseOperationException

class TaskRepository:
    """Repository class for managing Task entities in the database."""

    def __init__(self, db_session: Session) -> None:
        """Initialize the TaskRepository with a database session.

        Args:
            db_session (Session): SQLAlchemy session for database operations.
        """

        self.db_session = db_session
        self._logger = structlog.get_logger(__name__)

    # ------------------------------ CRUD operations ------------------------------

    # ------------------------------ Read operations ------------------------------

    def get_all(self, user_id: uuid.UUID) -> list[TaskModel]:
        """Retrieve all tasks for a given user ID.

        Args:
            user_id (uuid.UUID): Identifier of the user whose tasks should be returned.

        Returns:
            list[TaskModel]: A list of TaskModel instances for the requested user.

        Raises:
            DatabaseOperationException: When the database query fails.
        """
        
        try:
            self._logger.debug("tasks_repo.get_all", user_id=str(user_id))
            return self.db_session.query(TaskModel).filter(TaskModel.user_id == user_id).all()
        except Exception as e:
            raise DatabaseOperationException(f"Error retrieving tasks for user ID {user_id}: {str(e)}") from e
    
    def get_by_id(self, task_id: uuid.UUID, user_id: uuid.UUID) -> TaskModel:
        """Retrieve a task by task ID and owner ID.

        Args:
            task_id (uuid.UUID): Identifier of the task.
            user_id (uuid.UUID): Identifier of the user who owns the task.

        Returns:
            TaskModel: The task model instance if found.

        Raises:
            TaskNotFoundException: When the task does not exist for the user.
            DatabaseOperationException: When the database query fails.
        """
        
        try:
            self._logger.debug("tasks_repo.get_by_id", user_id=str(user_id), task_id=str(task_id))
            task: TaskModel | None = self.db_session.query(TaskModel) \
                                        .filter(TaskModel.id == task_id, TaskModel.user_id == user_id) \
                                        .first()
            if not task:
                raise TaskNotFoundException(task_id)
            return task
        except TaskNotFoundException:
            raise
        except Exception as e:
            raise DatabaseOperationException(f"Error retrieving task with ID {task_id}: {str(e)}") from e

    # ------------------------------ Write operations ------------------------------
    
    def create(self, task: TaskModel) -> TaskModel:
        """Persist a new task in the database.

        Args:
            task (TaskModel): The task entity to persist.

        Returns:
            TaskModel: The persisted task instance with generated fields populated.

        Raises:
            DatabaseOperationException: When the insert or commit fails.
        """

        try:
            self._logger.debug("tasks_repo.create", task_id=str(task.id), user_id=str(task.user_id))
            self.db_session.add(task)
            self.db_session.commit()
            self.db_session.refresh(task)
            self._logger.info("tasks_repo.create.success", task_id=str(task.id), user_id=str(task.user_id))
            return task
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseOperationException(f"Error creating task: {str(e)}") from e

    def update(self, task: TaskModel) -> TaskModel:
        """Persist updates to an existing task.

        Args:
            task (TaskModel): The task entity with updated fields.

        Returns:
            TaskModel: The updated task instance.

        Raises:
            DatabaseOperationException: When the commit or refresh fails.
        """
        
        try:
            self._logger.debug("tasks_repo.update", task_id=str(task.id), user_id=str(task.user_id))
            # merged_task = self.db_session.merge(task)
            self.db_session.commit()
            # self.db_session.refresh(merged_task)
            # return merged_task
            self.db_session.refresh(task)
            self._logger.info("tasks_repo.update.success", task_id=str(task.id), user_id=str(task.user_id))
            return task
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseOperationException(f"Error updating task with ID {task.id}: {str(e)}") from e

    def delete(self, task: TaskModel) -> None:
        """Delete a task from the database.

        Args:
            task (TaskModel): The task entity to delete.

        Raises:
            DatabaseOperationException: When the delete or commit fails.
        """

        try:
            self._logger.debug("tasks_repo.delete", task_id=str(task.id), user_id=str(task.user_id))
            self.db_session.delete(task)
            self.db_session.commit()
            self._logger.info("tasks_repo.delete.success", task_id=str(task.id), user_id=str(task.user_id))
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseOperationException(f"Error deleting task with ID {task.id}: {str(e)}") from e