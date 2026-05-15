import uuid
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

from tasks_router.routers.system_router import router as system_router
from tasks_router.schema.task_schema import TaskCreate
from tasks_router.schema.user_schema import User
from tasks_router.services.task_service import TaskServices
from tasks_router.services.user_service import UserService


class StubTaskRepository:
    def __init__(self) -> None:
        self.created_task = None

    def create(self, task):
        self.created_task = task
        return task


class StubUserModel:
    def __init__(self, username: str, display_name: str) -> None:
        self.username = username
        self.display_name = display_name


class StubUserRepository:
    def __init__(self, user: StubUserModel | None) -> None:
        self.user = user

    def get_by_id(self, username: str):
        if self.user and self.user.username == username:
            return self.user
        return None


def test_health_check_endpoint_returns_healthy_status() -> None:
    app = FastAPI()
    app.include_router(system_router)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"service": "tasks-api", "status": "healthy"}


def test_root_endpoint_returns_welcome_message_and_endpoints() -> None:
    app = FastAPI()
    app.include_router(system_router)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "Welcome to the Tasks API!"
    assert "/tasks" in payload["endpoints"]
    assert "/docs" in payload["endpoints"]


def test_user_schema_accepts_alias_fields() -> None:
    user = User.model_validate({"userName": "alice", "displayName": "Alice"})

    assert user.username == "alice"
    assert user.display_name == "Alice"


def test_task_service_create_returns_response_and_preserves_values() -> None:
    repository = StubTaskRepository()
    service = TaskServices(repository)
    user_id = uuid.uuid4()
    due_date = datetime(2030, 1, 1, tzinfo=UTC)

    result = service.create(
        TaskCreate(
            user_id=user_id,
            title="Write tests",
            status="todo",
            due_date=due_date,
        )
    )

    assert result.user_id == user_id
    assert result.title == "Write tests"
    assert result.status == "todo"
    assert result.due_date == due_date
    assert repository.created_task is not None


def test_user_service_get_user_returns_none_when_not_found() -> None:
    service = UserService(StubUserRepository(user=None))

    result = service.get_user("missing")

    assert result is None


def test_user_service_get_user_returns_schema_when_found() -> None:
    user_model = StubUserModel(username="alice", display_name="Alice")
    service = UserService(StubUserRepository(user=user_model))

    result = service.get_user("alice")

    assert result is not None
    assert result.username == "alice"
    assert result.display_name == "Alice"
