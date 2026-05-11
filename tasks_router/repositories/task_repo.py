"""
Repository module for managing Task entities in the database.
This module defines the TaskRepository class, which provides methods for performing CRUD operations on Task entities using SQLAlchemy ORM.
"""

import uuid

from sqlalchemy.orm import Session

from tasks_router.models.task_model import Task as TaskModel

class TaskRepository:
    """Repository class for managing Task entities in the database."""

    def __init__(self, db_session: Session) -> None:
        """Initialize the TaskRepository with a database session."""

        self.db_session = db_session

    # ------------------------------ CRUD operations ------------------------------

    # ------------------------------ Read operations ------------------------------

    def get_all(self, user_id: str) -> list[TaskModel]:
        """Retrieve all tasks for a given user ID."""
        
        try:
            return self.db_session.query(TaskModel).filter(TaskModel.user_id == user_id).all()
        except Exception:
            raise LookupError(f"Error occurred while fetching tasks for user ID: {user_id}")
    
    def get_by_id(self, task_id: uuid.UUID) -> TaskModel | None:
        """Retrieve a task by its ID."""
        
        try:
            return self.db_session.query(TaskModel).filter(TaskModel.id == task_id).first()
        except Exception:
            raise LookupError(f"Error occurred while fetching task with ID: {task_id}")

    # ------------------------------ Write operations ------------------------------
    
    def create(self, task: TaskModel) -> TaskModel:
        """Create a new task in the database."""

        try:
            self.db_session.add(task)
            self.db_session.commit()
            self.db_session.refresh(task)
            return task
        except Exception:
            self.db_session.rollback()
            raise RuntimeError("Error occurred while creating a new task.")
    
    def update(self, task: TaskModel) -> TaskModel:
        """Update an existing task in the database."""
        
        try:
            merged_task = self.db_session.merge(task) # Add logger here
            self.db_session.commit()
            self.db_session.refresh(merged_task)
            return merged_task
        except Exception:
            self.db_session.rollback()
            raise RuntimeError("Error occurred while updating the task.")

    def delete(self, task: TaskModel):
        """Delete a task from the database."""

        try:
            self.db_session.delete(task)
            self.db_session.commit()
        except Exception:
            self.db_session.rollback()
            raise RuntimeError("Error occurred while deleting the task.")