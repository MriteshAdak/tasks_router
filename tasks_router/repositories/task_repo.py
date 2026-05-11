"""
Repository module for managing Task entities in the database.
This module defines the TaskRepository class, which provides methods for performing CRUD operations on Task entities using SQLAlchemy ORM.
"""

from sqlalchemy.orm import Session

from tasks_router.models.task_model import Task as TaskModel
# from tasks_router.schema.task_base import Task as TaskSchema

class TaskRepository:
    """Repository class for managing Task entities in the database."""

    def __init__(self, db_session: Session) -> None:
        """Initialize the TaskRepository with a database session."""

        self.db_session = db_session

    # ------------------------------ CRUD operations ------------------------------

    # ------------------------------ Read operations ------------------------------

    def get(self, user_id: str) -> list[TaskModel] | bool:
        """Retrieve all tasks for a given user ID."""
        
        try:
            return self.db_session.query(TaskModel).filter(TaskModel.user_id == user_id).all()
        except Exception:
            return False
    
    def get_by_id(self, task_id: str) -> TaskModel | None | bool:
        """Retrieve a task by its ID."""
        
        try:
            return self.db_session.query(TaskModel).filter(TaskModel.id == task_id).first()
        except Exception:
            return False

    # ------------------------------ Write operations ------------------------------
    
    def create(self, task: TaskModel) -> TaskModel | bool:
        """Create a new task in the database."""

        try:
            self.db_session.add(task)
            self.db_session.commit()
            self.db_session.refresh(task)
            return task
        except Exception:
            self.db_session.rollback()
            return False
    
    def update(self, task: TaskModel) -> TaskModel | bool:
        """Update an existing task in the database."""
        
        try:
            merged_task = self.db_session.merge(task) # Add logger here
            self.db_session.commit()
            self.db_session.refresh(merged_task)
            return merged_task
        except Exception:
            self.db_session.rollback()
            return False
    
    def delete(self, task: TaskModel) -> bool:
        """Delete a task from the database."""

        try:
            self.db_session.delete(task)
            self.db_session.commit()
            return True
        except Exception:
            self.db_session.rollback()
            return False