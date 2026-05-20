import uuid
from unittest.mock import Mock

import pytest

from tasks_router.exceptions.custom_exceptions import (
    DatabaseOperationException,
    TaskNotFoundException,
    UserNotFoundException,
)
from tasks_router.models.task_model import Task
from tasks_router.models.user_model import User as UserModel
from tasks_router.repositories.task_repo import TaskRepository
from tasks_router.repositories.user_repo import UserRepository


def test_task_repository_get_all_returns_tasks() -> None:
    db_session = Mock()
    expected_tasks = [Mock(spec=Task)]
    db_session.query.return_value.filter.return_value.all.return_value = expected_tasks

    repository = TaskRepository(db_session)

    result = repository.get_all(uuid.uuid4())

    assert result == expected_tasks


def test_task_repository_get_by_id_raises_not_found() -> None:
    db_session = Mock()
    db_session.query.return_value.filter.return_value.first.return_value = None

    repository = TaskRepository(db_session)

    with pytest.raises(TaskNotFoundException):
        repository.get_by_id(uuid.uuid4(), uuid.uuid4())


def test_task_repository_get_by_id_wraps_database_error() -> None:
    db_session = Mock()
    db_session.query.side_effect = RuntimeError("query failed")

    repository = TaskRepository(db_session)

    with pytest.raises(DatabaseOperationException, match="Error retrieving task"):
        repository.get_by_id(uuid.uuid4(), uuid.uuid4())


def test_task_repository_create_persists_and_refreshes() -> None:
    db_session = Mock()
    task = Mock(spec=Task)
    repository = TaskRepository(db_session)

    result = repository.create(task)

    assert result is task
    db_session.add.assert_called_once_with(task)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(task)


def test_task_repository_create_rolls_back_on_error() -> None:
    db_session = Mock()
    db_session.commit.side_effect = RuntimeError("commit failed")
    repository = TaskRepository(db_session)

    with pytest.raises(DatabaseOperationException, match="Error creating task"):
        repository.create(Mock(spec=Task))

    db_session.rollback.assert_called_once()


def test_task_repository_update_rolls_back_on_error() -> None:
    db_session = Mock()
    db_session.commit.side_effect = RuntimeError("update failed")
    repository = TaskRepository(db_session)

    with pytest.raises(DatabaseOperationException, match="Error updating task"):
        repository.update(Mock(spec=Task))

    db_session.rollback.assert_called_once()


def test_task_repository_delete_rolls_back_on_error() -> None:
    db_session = Mock()
    db_session.commit.side_effect = RuntimeError("delete failed")
    repository = TaskRepository(db_session)

    with pytest.raises(DatabaseOperationException, match="Error deleting task"):
        repository.delete(Mock(spec=Task))

    db_session.rollback.assert_called_once()


def test_user_repository_get_all_returns_users() -> None:
    db_session = Mock()
    expected_users = [Mock(spec=UserModel)]
    db_session.query.return_value.all.return_value = expected_users

    repository = UserRepository(db_session)

    result = repository.get_all()

    assert result == expected_users


def test_user_repository_get_by_id_raises_not_found() -> None:
    db_session = Mock()
    db_session.query.return_value.filter.return_value.first.return_value = None

    repository = UserRepository(db_session)

    with pytest.raises(UserNotFoundException):
        repository.get_by_id("missing_user")


def test_user_repository_create_rolls_back_on_error() -> None:
    db_session = Mock()
    db_session.commit.side_effect = RuntimeError("commit failed")
    repository = UserRepository(db_session)

    with pytest.raises(
        DatabaseOperationException,
        match="Error occurred while creating a new user",
    ):
        repository.create(Mock(spec=UserModel))

    db_session.rollback.assert_called_once()
