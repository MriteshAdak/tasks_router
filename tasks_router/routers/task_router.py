"""
Task management API endpoints for CRUD operations on tasks.
"""

import uuid

import structlog
from fastapi import APIRouter, Depends, status, HTTPException

from tasks_router.services.task_service import TaskServices
from tasks_router.schema.task_schema import TaskCreate, TaskUpdate, TaskResponse
from tasks_router.auth_placeholder import get_current_user_id
from tasks_router.dependencies import get_task_services
from tasks_router.exceptions.custom_exceptions import DatabaseOperationException, TaskNotFoundException, ServiceException

router: APIRouter = APIRouter(prefix="/tasks", tags=["Tasks"])
logger = structlog.get_logger(__name__)

@router.get(
        "/",
        response_model=list[TaskResponse],
        status_code=status.HTTP_200_OK,
    )
def get_tasks(
    user_id: uuid.UUID = Depends(get_current_user_id),
    task_services: TaskServices = Depends(get_task_services)
    ) -> list[TaskResponse]:
    """Retrieve all tasks for the authenticated user.

    This endpoint returns all task records that belong to the authenticated user.

    Args:
        user_id (uuid.UUID): Current authenticated user's identifier, injected by dependency.
        task_services (TaskServices): Task service dependency used to fetch task data.

    Returns:
        list[TaskResponse]: A list of task response objects for the authenticated user.

    Raises:
        HTTPException: 500 if a database operation fails.
        HTTPException: 400 if a service-layer validation or business rule fails.

    Status Codes:
        200: Tasks retrieved successfully.
    """

    try:
        logger.info("Retrieving all tasks", user_id=str(user_id))
        tasks = task_services.get_all(user_id)
        logger.info("Tasks retrieved", user_id=str(user_id), task_count=len(tasks))
        return tasks
    except DatabaseOperationException as e:
        logger.error("DB Ops error while retrieving tasks", user_id=str(user_id), error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ServiceException as e:
        logger.error("Service error while retrieving tasks", user_id=str(user_id), error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error while retrieving tasks", user_id=str(user_id))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while retrieving tasks") from e


@router.post(
        "/",
        response_model=TaskResponse,
        status_code=status.HTTP_201_CREATED
    )
def create_task(
    task: TaskCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    task_services: TaskServices = Depends(get_task_services)
    ) -> TaskResponse:
    """Create a new task for the authenticated user.

    This endpoint accepts a TaskCreate payload and persists a new task for the authenticated user.

    Args:
        task (TaskCreate): Payload containing task title, status, and optional due date.
        user_id (uuid.UUID): Current authenticated user's identifier, injected by dependency.
        task_services (TaskServices): Task service dependency used to persist the new task.

    Returns:
        TaskResponse: The created task representation.

    Raises:
        HTTPException: 500 if a database operation fails.
        HTTPException: 400 if a service-layer validation or business rule fails.

    Status Codes:
        201: Task created successfully.
    """

    try:
        logger.info("Creating new task", user_id=str(user_id))
        created_task: TaskResponse = task_services.create(task, user_id)
        logger.info("Task created", user_id=str(user_id), task_id=str(created_task.id))
        return created_task
    except DatabaseOperationException as e:
        logger.error("DB Ops error while creating task", user_id=str(user_id), error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ServiceException as e:
        logger.error("Service error while creating task", user_id=str(user_id), error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error while creating task", user_id=str(user_id))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while creating the task") from e


@router.patch(
        "/{task_id}",
        response_model=TaskResponse,
        status_code=status.HTTP_200_OK
    )
def update_task(
    task_id: uuid.UUID,
    task: TaskUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    task_services: TaskServices = Depends(get_task_services)
    ) -> TaskResponse:
    """Update an existing task for the authenticated user.

    Args:
        task_id (uuid.UUID): Identifier of the task to update, passed as a path parameter.
        task (TaskUpdate): Payload containing task fields to update.
        user_id (uuid.UUID): Current authenticated user's identifier, injected by dependency.
        task_services (TaskServices): Task service dependency used to apply changes.

    Returns:
        TaskResponse: The updated task representation.

    Raises:
        HTTPException: 404 if the requested task does not exist for the authenticated user.
        HTTPException: 500 if a database operation fails.
        HTTPException: 400 if a service-layer validation or business rule fails.

    Status Codes:
        200: Task updated successfully.
        404: Task not found.
    """

    try:
        logger.info("Updating task", user_id=str(user_id), task_id=str(task_id))
        updated_task: TaskResponse = task_services.update(task_id, user_id, task)
        logger.info("Task updated", user_id=str(user_id), task_id=str(task_id))
        return updated_task
    except TaskNotFoundException:
        logger.warning("Task not found", user_id=str(user_id), task_id=str(task_id))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID {task_id} not found")
    except DatabaseOperationException as e:
        logger.error("DB Ops error while updating task", user_id=str(user_id), task_id=str(task_id), error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ServiceException as e:
        logger.error("Service error while updating task", user_id=str(user_id), task_id=str(task_id), error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error while updating task", user_id=str(user_id), task_id=str(task_id))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while updating the task") from e

@router.delete(
        "/{task_id}",
        status_code=status.HTTP_204_NO_CONTENT
    )
def delete_task(
    task_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    task_services: TaskServices = Depends(get_task_services)
    ) -> None:
    """Delete a task for the authenticated user by its identifier.

    Args:
        task_id (uuid.UUID): Identifier of the task to delete, passed as a path parameter.
        user_id (uuid.UUID): Current authenticated user's identifier, injected by dependency.
        task_services (TaskServices): Task service dependency used to remove the task.

    Raises:
        HTTPException: 404 if the requested task does not exist for the authenticated user.
        HTTPException: 500 if a database operation fails.
        HTTPException: 400 if a service-layer validation or business rule fails.

    Status Codes:
        204: Task deleted successfully.
        404: Task not found.
    """
    
    try:
        logger.info("Deleting task", user_id=str(user_id), task_id=str(task_id))
        task_services.delete(task_id, user_id)
        logger.info("Task deleted", user_id=str(user_id), task_id=str(task_id))
    except TaskNotFoundException:
        logger.warning("Task not found", user_id=str(user_id), task_id=str(task_id))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID {task_id} not found")
    except DatabaseOperationException as e:
        logger.error("DB Ops error while deleting task", user_id=str(user_id), task_id=str(task_id), error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ServiceException as e:
        logger.error("Service error while deleting task", user_id=str(user_id), task_id=str(task_id), error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error while deleting task", user_id=str(user_id), task_id=str(task_id))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while deleting the task") from e