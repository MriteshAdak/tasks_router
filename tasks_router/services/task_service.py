"""
TaskServices class that provides business logic for task management operations.
This module defines the TaskServices class, which interacts with the TaskRepository to perform CRUD operations on Task entities. The TaskServices class also handles the conversion of TaskModel instances to TaskResponse schemas for API responses.
"""

import uuid

from tasks_router.models.task_model import Task as TaskModel
from tasks_router.schema.task_schema import TaskCreate, TaskUpdate, TaskResponse
from tasks_router.repositories.task_repo import TaskRepository
from tasks_router.utils import convert_task_model_to_response, convert_task_models_to_responses

class TaskServices:
    def __init__(self, repository: TaskRepository) -> None:
        """Initialize the TaskServices with a TaskRepository instance."""
        
        self.repository = repository

    def get_all(self, user_id: uuid.UUID) -> list[TaskResponse]:
        """Service for retrieving all tasks for a given user ID."""

        queried_tasks: list[TaskModel] =  self.repository.get_all(user_id)
        return convert_task_models_to_responses(queried_tasks)
    
    def create(self, task: TaskCreate) -> TaskResponse:
        """Service for creating a new task in the database."""
        
        new_task = TaskModel(
            id=str(uuid.uuid4()),
            user_id=task.user_id,
            title=task.title,
            status=task.status,
            due_date=task.due_date if task.due_date else None
        )
        created_task: TaskModel = self.repository.create(new_task)
        return convert_task_model_to_response(created_task)
    
    def update(self, task: TaskUpdate) -> TaskResponse:
        """Service for updating an existing task in the database."""

        existing_task: TaskModel | None = self.repository.get_by_id(task.id)

        if not existing_task:
            raise ValueError(f"Task with ID {task.id} not found.")

        existing_task.title = task.title
        existing_task.status = task.status
        existing_task.due_date = task.due_date if task.due_date else None
        
        return convert_task_model_to_response(self.repository.update(existing_task))
        
    
    def delete(self, task: TaskUpdate):
        """Service for deleting a task from the database."""

        existing_task: TaskModel | None = self.repository.get_by_id(task.id)

        if not existing_task:
            raise ValueError(f"Task with ID {task.id} not found.")
        self.repository.delete(existing_task)