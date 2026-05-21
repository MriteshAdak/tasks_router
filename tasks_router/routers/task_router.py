"""
Task management API endpoints for CRUD operations on tasks.
"""

import uuid

from fastapi import APIRouter, Depends, status, HTTPException

from tasks_router.services.task_service import TaskServices
from tasks_router.schema.task_schema import TaskCreate, TaskUpdate, TaskResponse
from tasks_router.auth_placeholder import get_current_user_id
from tasks_router.dependencies import get_task_services
from tasks_router.exceptions.custom_exceptions import DatabaseOperationException, TaskNotFoundException, ServiceException

router: APIRouter = APIRouter(prefix="/tasks", tags=["Tasks"])

# TODO:
# 1. Add auth dependencies so users can only access their own tasks.
# 2. Align router contracts with model/schema updates so user_id
#    remains injected from auth instead of request body payloads.
# We keep placeholder auth to preserve endpoint shape until identity
# integration lands, which avoids breaking API clients during rollout.

@router.get(
        "/",
        response_model=list[TaskResponse],
        status_code=status.HTTP_200_OK,
    )
def get_tasks(
    user_id: uuid.UUID = Depends(get_current_user_id),
    task_services: TaskServices = Depends(get_task_services)
    ) -> list[TaskResponse]:
    """Fetch all tasks for the current user.

    Args:
        user_id: Auth-scoped user identifier.
        task_services: Injected task service dependency.

    Returns:
        Task DTO list for API responses.

    Raises:
        HTTPException: If service or database operations fail.
    """

    try:
        return task_services.get_all(user_id)
    except DatabaseOperationException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
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
    """Create a task for the current user.

    Args:
        task: Task payload from request body.
        user_id: Auth-scoped user identifier.
        task_services: Injected task service dependency.

    Returns:
        Persisted task DTO.

    Raises:
        HTTPException: If service or database operations fail.
    """

    try:
        created_task: TaskResponse = task_services.create(task, user_id)
        return created_task
    except DatabaseOperationException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
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
    """Update an existing task for the current user.

    Args:
        task_id: Task identifier from route path.
        task: Partial task payload from request body.
        user_id: Auth-scoped user identifier.
        task_services: Injected task service dependency.

    Returns:
        Updated task DTO.

    Raises:
        HTTPException: If lookup or update operations fail.
    """

    try:
        updated_task: TaskResponse = task_services.update(task_id, user_id, task)
        return updated_task
    except TaskNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID {task_id} not found")
    except DatabaseOperationException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
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
    """Delete a task for the current user.

    Args:
        task_id: Task identifier from route path.
        user_id: Auth-scoped user identifier.
        task_services: Injected task service dependency.

    Raises:
        HTTPException: If lookup or deletion operations fail.
    """
    
    try:
        task_services.delete(task_id, user_id)
    except TaskNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID {task_id} not found")
    except DatabaseOperationException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while deleting the task") from e
