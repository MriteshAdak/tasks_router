"""
TaskServices class that provides business logic for task management operations.
This module defines the TaskServices class, which interacts with the TaskRepository to perform CRUD operations on Task entities. The TaskServices class also handles the conversion of TaskModel instances to TaskResponse schemas for API responses.
"""

import uuid

import structlog
from tasks_router.models.task_model import Task as TaskModel
from tasks_router.schema.task_schema import TaskCreate, TaskUpdate, TaskResponse
from tasks_router.repositories.task_repo import TaskRepository
from tasks_router.utils import convert_task_model_to_response_dto, convert_task_models_to_responses_dto
from tasks_router.exceptions.custom_exceptions import TaskNotFoundException, DatabaseOperationException, ServiceException

class TaskServices:
    """Business service layer for task CRUD operations.

    This class handles task creation, retrieval, update, and deletion by delegating persistence operations to the TaskRepository.
    """

    def __init__(self, repository: TaskRepository) -> None:
        """Initialize the TaskServices with a TaskRepository instance.

        Args:
            repository (TaskRepository): Repository used to interact with task persistence.
        """
        
        self.repository = repository
        self._logger = structlog.get_logger(__name__)

    def get_all(self, user_id: uuid.UUID) -> list[TaskResponse]:
        """Retrieve all tasks for a given user.

        Args:
            user_id (uuid.UUID): Identifier of the user whose tasks are requested.

        Returns:
            list[TaskResponse]: A list of task response DTOs for the supplied user ID.

        Raises:
            DatabaseOperationException: When there is an error communicating with the database.
            ServiceException: When an unexpected service-layer error occurs.
        """

        try:
            self._logger.debug("task_services.get_all", user_id=str(user_id))
            queried_tasks: list[TaskModel] =  self.repository.get_all(user_id)
            if not queried_tasks:
                self._logger.info("task_services.get_all.empty", user_id=str(user_id))
                return []
            responses = convert_task_models_to_responses_dto(queried_tasks)
            self._logger.info("task_services.get_all.success", user_id=str(user_id), task_count=len(responses))
            return responses
        except DatabaseOperationException:
            raise
        except Exception as e:
            raise ServiceException(f"Error retrieving tasks for user ID {user_id}: {str(e)}") from e


    def create(self, task: TaskCreate, user_id: uuid.UUID) -> TaskResponse:
        """Create a new task for the specified user.

        Args:
            task (TaskCreate): DTO containing title, status, and optional due date.
            user_id (uuid.UUID): Identifier of the user for whom the task is created.

        Returns:
            TaskResponse: Task response DTO representing the created task.

        Raises:
            DatabaseOperationException: When the task cannot be persisted.
            ServiceException: When an unexpected service-layer error occurs.
        """
        
        # TODO: 
        # 1. Add validation to ensure that the user_id exists in the database before creating a task.
        # 2. Add validation for due date to ensure that it is not set to a past date.

        new_task_data: dict[str, object] = task.model_dump(exclude_unset=True)
        new_task_data['user_id'] = user_id
        new_task: TaskModel = TaskModel(**new_task_data)

        try:
            self._logger.debug("task_services.create", user_id=str(user_id))
            created_task: TaskModel = self.repository.create(new_task)
            response = convert_task_model_to_response_dto(created_task)
            self._logger.info("task_services.create.success", user_id=str(user_id), task_id=str(created_task.id))
            return response
        except DatabaseOperationException:
            raise
        except Exception as e:
            raise ServiceException(f"Error creating task for user ID {user_id}: {str(e)}") from e


    def update(self, task_id: uuid.UUID, user_id: uuid.UUID, task: TaskUpdate) -> TaskResponse:
        """Update an existing task belonging to the specified user.

        Args:
            task_id (uuid.UUID): Identifier of the task to update.
            user_id (uuid.UUID): Identifier of the user who owns the task.
            task (TaskUpdate): DTO containing fields to update.

        Returns:
            TaskResponse: Task response DTO representing the updated task.

        Raises:
            TaskNotFoundException: When the task does not exist for the user.
            DatabaseOperationException: When there is an error communicating with the database.
            ServiceException: When an unexpected service-layer error occurs.
        """

        try:
            self._logger.debug("task_services.update.lookup", user_id=str(user_id), task_id=str(task_id))
            existing_task: TaskModel = self.repository.get_by_id(task_id, user_id)
        except TaskNotFoundException:
            raise
        except DatabaseOperationException:
            raise

        updated_task_data: dict[str, object] = task.model_dump(exclude_unset=True)
        for key, value in updated_task_data.items():
            setattr(existing_task, key, value)
        
        try:
            self._logger.debug("task_services.update", user_id=str(user_id), task_id=str(task_id))
            updated_task: TaskModel = self.repository.update(existing_task)
            response = convert_task_model_to_response_dto(updated_task)
            self._logger.info("task_services.update.success", user_id=str(user_id), task_id=str(task_id))
            return response
        except DatabaseOperationException:
            raise
        except Exception as e:
            raise ServiceException(f"Error updating task with ID {task_id}: {str(e)}") from e


    def delete(self, task_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Delete a task belonging to the specified user.

        Args:
            task_id (uuid.UUID): Identifier of the task to delete.
            user_id (uuid.UUID): Identifier of the user who owns the task.

        Raises:
            TaskNotFoundException: When the task does not exist for the user.
            DatabaseOperationException: When there is an error communicating with the database.
            ServiceException: When an unexpected service-layer error occurs.
        """

        try:
            self._logger.debug("task_services.delete.lookup", user_id=str(user_id), task_id=str(task_id))
            existing_task: TaskModel = self.repository.get_by_id(task_id, user_id)
        except TaskNotFoundException:
            raise
        except DatabaseOperationException:
            raise

        try:
            self._logger.debug("task_services.delete", user_id=str(user_id), task_id=str(task_id))
            self.repository.delete(existing_task)
            self._logger.info("task_services.delete.success", user_id=str(user_id), task_id=str(task_id))
        except DatabaseOperationException:
            raise
        except Exception as e:
            raise ServiceException(f"Error deleting task with ID {task_id}: {str(e)}") from e