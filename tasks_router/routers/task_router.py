import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from tasks_router.services.task_service import TaskServices
from tasks_router.repositories.task_repo import TaskRepository
from tasks_router.schema.task_schema import TaskCreate, TaskUpdate, TaskResponse
from tasks_router.database.initiate_db import Database
from tasks_router.database.config_db import settings

router: APIRouter = APIRouter(prefix="/tasks", tags=["Tasks"])

_db = Database(settings)

@router.get("/", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
def get_tasks(user_id: uuid.UUID, db: Session = Depends(_db.get_db)) -> list[TaskResponse]:
    task_services = TaskServices(TaskRepository(db))
    return task_services.get_all(user_id)

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(_db.get_db)) -> TaskResponse:
    task_services = TaskServices(TaskRepository(db))
    return task_services.create(task)

@router.put("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_task(task_id: uuid.UUID, task: TaskUpdate, db: Session = Depends(_db.get_db)) -> TaskResponse:
    task_services = TaskServices(TaskRepository(db))
    return task_services.update(task_id, task)

@router.delete("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def delete_task(task_id: uuid.UUID, db: Session = Depends(_db.get_db)) -> None:
    task_services = TaskServices(TaskRepository(db))
    task_services.delete(task_id)