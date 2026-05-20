import uuid
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from tasks_router.auth_placeholder import get_current_user_id
from tasks_router.dependencies import get_task_services, get_user_services
from tasks_router.enums.task_statuses import TaskStatus
from tasks_router.exceptions.custom_exceptions import (
    DatabaseOperationException,
    TaskNotFoundException,
)
from tasks_router.routers.system_router import router as system_router
from tasks_router.routers.task_router import router as task_router
from tasks_router.routers.user_router import router as user_router
from tasks_router.schema.task_schema import TaskResponse
from tasks_router.schema.user_schema import User


def _task_test_client(task_service: Mock, user_id: uuid.UUID) -> TestClient:
    app = FastAPI()
    app.include_router(task_router)
    app.dependency_overrides[get_task_services] = lambda: task_service
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    return TestClient(app)


def _user_test_client(user_service: Mock) -> TestClient:
    app = FastAPI()
    app.include_router(user_router)
    app.dependency_overrides[get_user_services] = lambda: user_service
    return TestClient(app)


def test_system_router_health_and_root() -> None:
    app = FastAPI()
    app.include_router(system_router)

    with TestClient(app) as client:
        health = client.get("/health")
        root = client.get("/")

    assert health.status_code == 200
    assert health.json() == {"service": "tasks-api", "status": "healthy"}
    assert root.status_code == 200
    assert "/tasks" in root.json()["endpoints"]


def test_get_tasks_success() -> None:
    user_id = uuid.uuid4()
    task = TaskResponse(
        id=uuid.uuid4(),
        title="Read docs",
        status=TaskStatus.TODO,
        due_date=None,
    )
    task_service = Mock()
    task_service.get_all.return_value = [task]

    with _task_test_client(task_service, user_id) as client:
        response = client.get("/tasks/")

    assert response.status_code == 200
    assert response.json()[0]["id"] == str(task.id)


def test_update_task_not_found_maps_to_404() -> None:
    user_id = uuid.uuid4()
    task_id = uuid.uuid4()
    task_service = Mock()
    task_service.update.side_effect = TaskNotFoundException(task_id)

    with _task_test_client(task_service, user_id) as client:
        response = client.patch(f"/tasks/{task_id}", json={"title": "Updated"})

    assert response.status_code == 404
    assert response.json()["detail"] == f"Task with ID {task_id} not found"


def test_create_task_database_error_maps_to_500() -> None:
    task_service = Mock()
    task_service.create.side_effect = DatabaseOperationException("db failure")

    with _task_test_client(task_service, uuid.uuid4()) as client:
        response = client.post("/tasks/", json={"title": "New task"})

    assert response.status_code == 500
    assert response.json()["detail"] == "db failure"


def test_get_user_success() -> None:
    user_service = Mock()
    user = User(id=uuid.uuid4(), username="alice", display_name="Alice")
    user_service.get_user.return_value = user

    with _user_test_client(user_service) as client:
        response = client.get("/users/alice")

    assert response.status_code == 200
    assert response.json() == {
        "id": str(user.id),
        "username": "alice",
        "display_name": "Alice",
    }


def test_get_user_not_found_maps_to_404() -> None:
    user_service = Mock()
    from tasks_router.exceptions.custom_exceptions import UserNotFoundException

    user_service.get_user.side_effect = UserNotFoundException("alice")

    with _user_test_client(user_service) as client:
        response = client.get("/users/alice")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
