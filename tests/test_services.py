import uuid
from unittest.mock import Mock

import pytest

from tasks_router.enums.task_statuses import TaskStatus
from tasks_router.exceptions.custom_exceptions import (
    DatabaseOperationException,
    ServiceException,
    TaskNotFoundException,
    UserNotFoundException,
)
from tasks_router.models.task_model import Task
from tasks_router.models.user_model import User as UserModel
from tasks_router.schema.task_schema import TaskCreate, TaskUpdate
from tasks_router.schema.user_schema import User
from tasks_router.services.task_service import TaskServices
from tasks_router.services.user_service import UserService


def test_task_service_get_all_returns_empty_list() -> None:
    repository = Mock()
    repository.get_all.return_value = []

    service = TaskServices(repository)

    assert service.get_all(uuid.uuid4()) == []


def test_task_service_create_sets_user_id_and_returns_response() -> None:
    repository = Mock()
    user_id = uuid.uuid4()
    created = Task(
        id=uuid.uuid4(),
        user_id=user_id,
        title="Create test",
        status=TaskStatus.TODO,
        due_date=None,
    )
    repository.create.return_value = created
    service = TaskServices(repository)

    response = service.create(TaskCreate(title="Create test"), user_id)

    saved_task = repository.create.call_args.args[0]
    assert saved_task.user_id == user_id
    assert response.id == created.id
    assert response.title == "Create test"


def test_task_service_update_propagates_not_found() -> None:
    repository = Mock()
    repository.get_by_id.side_effect = TaskNotFoundException(uuid.uuid4())
    service = TaskServices(repository)

    with pytest.raises(TaskNotFoundException):
        service.update(uuid.uuid4(), uuid.uuid4(), TaskUpdate(title="Updated"))


def test_task_service_delete_wraps_unexpected_exception() -> None:
    repository = Mock()
    repository.get_by_id.return_value = Task(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="Delete test",
        status=TaskStatus.TODO,
        due_date=None,
    )
    repository.delete.side_effect = RuntimeError("boom")
    service = TaskServices(repository)

    with pytest.raises(ServiceException, match="Error deleting task"):
        service.delete(uuid.uuid4(), uuid.uuid4())


def test_task_service_get_all_propagates_database_exception() -> None:
    repository = Mock()
    repository.get_all.side_effect = DatabaseOperationException("db failure")
    service = TaskServices(repository)

    with pytest.raises(DatabaseOperationException):
        service.get_all(uuid.uuid4())


def test_user_service_get_user_propagates_not_found() -> None:
    repository = Mock()
    repository.get_by_id.side_effect = UserNotFoundException("unknown")
    service = UserService(repository)

    with pytest.raises(UserNotFoundException):
        service.get_user("unknown")


def test_user_service_create_wraps_unexpected_exception() -> None:
    repository = Mock()
    repository.create.side_effect = RuntimeError("insert error")
    service = UserService(repository)

    with pytest.raises(ServiceException, match="Error creating user"):
        service.create(User(id=uuid.uuid4(), username="alice", display_name="Alice"))


def test_user_service_create_returns_user_dto() -> None:
    repository = Mock()
    user_model = UserModel(
        id=uuid.uuid4(),
        username="alice",
        display_name="Alice",
    )
    repository.create.return_value = user_model
    service = UserService(repository)

    result = service.create(
        User(id=user_model.id, username="alice", display_name="Alice")
    )

    assert result.id == user_model.id
    assert result.username == "alice"
