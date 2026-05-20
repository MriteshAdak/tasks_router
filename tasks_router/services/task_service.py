"""
Task service business logic for task management operations.

The service translates repository models into API schema DTOs.
"""

import uuid

from tasks_router.models.task_model import Task as TaskModel
from tasks_router.schema.task_schema import TaskCreate, TaskUpdate, TaskResponse
from tasks_router.repositories.task_repo import TaskRepository
from tasks_router.utils import convert_task_model_to_response_dto, convert_task_models_to_responses_dto
from tasks_router.exceptions.custom_exceptions import TaskNotFoundException, DatabaseOperationException, ServiceException

class TaskServices:
    def __init__(self, repository: TaskRepository) -> None:
        """Initialize the task service.

        Args:
            repository: Task repository dependency.
        """
        self.repository = repository

    def get_all(self, user_id: uuid.UUID) -> list[TaskResponse]:
        """Return all tasks for a user.

        Args:
            user_id: User identifier used for scoped retrieval.

        Returns:
            Task DTOs for API responses.

        Raises:
            DatabaseOperationException: If repository access fails.
            ServiceException: If an unexpected service error occurs.
        """

        try:
            queried_tasks: list[TaskModel] =  self.repository.get_all(user_id)
            if not queried_tasks:
                return []
            return convert_task_models_to_responses_dto(queried_tasks)
        except DatabaseOperationException:
            raise
        except Exception as e:
            raise ServiceException(f"Error retrieving tasks for user ID {user_id}: {str(e)}") from e


    def create(self, task: TaskCreate, user_id: uuid.UUID) -> TaskResponse:
        """Create and return a task for a user.

        Args:
            task: Task DTO from the API layer.
            user_id: User identifier that owns the task.

        Returns:
            Persisted task DTO for API responses.

        Raises:
            DatabaseOperationException: If repository persistence fails.
            ServiceException: If an unexpected service error occurs.
        """

        # Validation is deferred to avoid duplicating upcoming user and
        # date policies that will be centralized in one validator.

        new_task_data: dict[str, object] = task.model_dump(exclude_unset=True)
        new_task_data['user_id'] = user_id
        new_task: TaskModel = TaskModel(**new_task_data)

        try:
            created_task: TaskModel = self.repository.create(new_task)
            return convert_task_model_to_response_dto(created_task)
        except DatabaseOperationException:
            raise
        except Exception as e:
            raise ServiceException(f"Error creating task for user ID {user_id}: {str(e)}") from e


    def update(self, task_id: uuid.UUID, user_id: uuid.UUID, task: TaskUpdate) -> TaskResponse:
        """Update and return an existing user task.

        Args:
            task_id: Task identifier to update.
            user_id: User identifier used for scoped access.
            task: Partial task DTO with fields to update.

        Returns:
            Updated task DTO for API responses.

        Raises:
            TaskNotFoundException: If the task cannot be found.
            DatabaseOperationException: If repository access fails.
            ServiceException: If an unexpected service error occurs.
        """

        try:
            existing_task: TaskModel = self.repository.get_by_id(task_id, user_id)
        except TaskNotFoundException:
            raise
        except DatabaseOperationException:
            raise

        updated_task_data: dict[str, object] = task.model_dump(exclude_unset=True)
        for key, value in updated_task_data.items():
            setattr(existing_task, key, value)
        
        try:
            updated_task: TaskModel = self.repository.update(existing_task)
            return convert_task_model_to_response_dto(updated_task)
        except DatabaseOperationException:
            raise
        except Exception as e:
            raise ServiceException(f"Error updating task with ID {task_id}: {str(e)}") from e


    def delete(self, task_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Delete an existing user task.

        Args:
            task_id: Task identifier to delete.
            user_id: User identifier used for scoped access.

        Raises:
            TaskNotFoundException: If the task cannot be found.
            DatabaseOperationException: If repository access fails.
            ServiceException: If an unexpected service error occurs.
        """

        try:
            existing_task: TaskModel = self.repository.get_by_id(task_id, user_id)
        except TaskNotFoundException:
            raise
        except DatabaseOperationException:
            raise

        try:
            self.repository.delete(existing_task)
        except DatabaseOperationException:
            raise
        except Exception as e:
            raise ServiceException(f"Error deleting task with ID {task_id}: {str(e)}") from e
