"""
Task management API endpoints for CRUD operations on tasks.
"""

import uuid

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from tasks_router.services.task_service import TaskServices
from tasks_router.repositories.task_repo import TaskRepository
from tasks_router.schema.task_schema import TaskCreate, TaskUpdate, TaskResponse
from tasks_router.database.initiate_db import Database
from tasks_router.database.config_db import settings
from tasks_router.dependencies.auth_placeholder import get_current_user_id
from tasks_router.exceptions.custom_exceptions import DatabaseOperationException, TaskNotFoundException, ServiceException

router: APIRouter = APIRouter(prefix="/tasks", tags=["Tasks"])

_db = Database(settings)

# TODO: 
# 1. Add authentication and authorization dependencies to ensure that users can only access their own tasks.
# 2. Update routers per the new updates to the models and schemas. user_id should be passed separately from the request body using the placeholder auth module.

@router.get(
        "/",
        response_model=list[TaskResponse],
        status_code=status.HTTP_200_OK,
    )
def get_tasks(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(_db.get_db),
    ) -> list[TaskResponse]:
    """Endpoint to retrieve all tasks for a given user ID."""

    try:
        task_services: TaskServices = TaskServices(TaskRepository(db))
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
    db: Session = Depends(_db.get_db)
    ) -> TaskResponse:
    """Endpoint to create a new task."""

    try:
        task_services: TaskServices = TaskServices(TaskRepository(db))
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
    db: Session = Depends(_db.get_db)
    ) -> TaskResponse:
    """Endpoint to update an existing task."""

    try:
        task_services: TaskServices = TaskServices(TaskRepository(db))
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
    db: Session = Depends(_db.get_db)
    ) -> None:
    """Endpoint to delete a task by ID."""
    
    try:
        task_services: TaskServices = TaskServices(TaskRepository(db))
        task_services.delete(task_id, user_id)
    except TaskNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID {task_id} not found")
    except DatabaseOperationException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while deleting the task") from e