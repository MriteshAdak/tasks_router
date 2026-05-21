"""
Repository module for managing Task entities in the database.

This module defines TaskRepository methods for SQLAlchemy CRUD
operations on tasks.
"""

import uuid

from sqlalchemy.orm import Session

from tasks_router.models.task_model import Task as TaskModel
from tasks_router.exceptions.custom_exceptions import TaskNotFoundException, DatabaseOperationException

class TaskRepository:
    """Repository class for managing Task entities in the database."""

    def __init__(self, db_session: Session) -> None:
        """Initialize the TaskRepository with a database session."""

        self.db_session = db_session

    # CRUD operation sections keep repository responsibilities grouped.

    # Read operations provide user-scoped task retrieval methods.

    def get_all(self, user_id: uuid.UUID) -> list[TaskModel]:
        """Retrieve tasks for a user.

        Args:
            user_id: Owner identifier used for task scoping.

        Returns:
            All tasks for the provided user.

        Raises:
            DatabaseOperationException: If the database query fails.
        """
        try:
            return self.db_session.query(TaskModel).filter(TaskModel.user_id == user_id).all()
        except Exception as e:
            raise DatabaseOperationException(f"Error retrieving tasks for user ID {user_id}: {str(e)}") from e

    def get_by_id(self, task_id: uuid.UUID, user_id: uuid.UUID) -> TaskModel:
        """Retrieve a task by ID for a specific user.

        Args:
            task_id: Task identifier for lookup.
            user_id: Owner identifier used for access scoping.

        Returns:
            The matching task model.

        Raises:
            TaskNotFoundException: If no scoped task exists.
            DatabaseOperationException: If the database query fails.
        """
        try:
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

    # Write operations mutate database state for task entities.
    def create(self, task: TaskModel) -> TaskModel:
        """Create a task record.

        Args:
            task: Task model prepared for persistence.

        Returns:
            The persisted and refreshed task model.

        Raises:
            DatabaseOperationException: If persistence fails.
        """

        try:
            self.db_session.add(task)
            self.db_session.commit()
            self.db_session.refresh(task)
            return task
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseOperationException(f"Error creating task: {str(e)}") from e

    def update(self, task: TaskModel) -> TaskModel:
        """Update an existing task.

        Args:
            task: Task model containing latest state.

        Returns:
            The refreshed task model after commit.

        Raises:
            DatabaseOperationException: If update persistence fails.
        """
        try:
            # merged_task = self.db_session.merge(task)
            self.db_session.commit()
            # self.db_session.refresh(merged_task)
            # return merged_task
            self.db_session.refresh(task)
            return task
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseOperationException(f"Error updating task with ID {task.id}: {str(e)}") from e

    def delete(self, task: TaskModel) -> None:
        """Delete a task.

        Args:
            task: Persisted task model to remove.

        Raises:
            DatabaseOperationException: If delete persistence fails.
        """

        try:
            self.db_session.delete(task)
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseOperationException(f"Error deleting task with ID {task.id}: {str(e)}") from e
