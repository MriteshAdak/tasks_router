import uuid
from unittest.mock import Mock

import pytest

from tasks_router.exceptions.custom_exceptions import (
    DatabaseOperationException,
    TaskNotFoundException,
    UserNotFoundException,
)
from tasks_router.models.task_model import Task as TaskModel
from tasks_router.models.user_model import User as UserModel
from tasks_router.repositories.task_repo import TaskRepository
from tasks_router.repositories.user_repo import UserRepository


def test_task_repository_get_all_returns_tasks_and_filters_by_user_id() -> None:
    # Arrange
    db_session = Mock()
    expected_tasks = [Mock(spec=TaskModel), Mock(spec=TaskModel)]
    user_id = uuid.uuid4()
    db_session.query.return_value.filter.return_value.all.return_value = expected_tasks
    repository = TaskRepository(db_session)

    # Act
    result = repository.get_all(user_id)

    # Assert
    assert result == expected_tasks
    db_session.query.assert_called_once_with(TaskModel)
    db_session.query.return_value.filter.assert_called_once()
    filter_args = db_session.query.return_value.filter.call_args.args
    assert len(filter_args) == 1
    assert filter_args[0].left.key == "user_id"
    assert filter_args[0].right.value == user_id
    db_session.query.return_value.filter.return_value.all.assert_called_once_with()


def test_task_repository_get_all_wraps_database_errors() -> None:
    # Arrange
    db_session = Mock()
    db_session.query.side_effect = RuntimeError("query failed")
    repository = TaskRepository(db_session)

    # Act / Assert
    with pytest.raises(DatabaseOperationException, match="Error retrieving tasks"):
        repository.get_all(uuid.uuid4())


def test_task_repository_get_by_id_returns_task_and_filters_by_ids() -> None:
    # Arrange
    db_session = Mock()
    user_id = uuid.uuid4()
    task_id = uuid.uuid4()
    task = Mock(spec=TaskModel)
    db_session.query.return_value.filter.return_value.first.return_value = task
    repository = TaskRepository(db_session)

    # Act
    result = repository.get_by_id(task_id, user_id)

    # Assert
    assert result is task
    db_session.query.assert_called_once_with(TaskModel)
    db_session.query.return_value.filter.assert_called_once()
    filter_args = db_session.query.return_value.filter.call_args.args
    assert len(filter_args) == 2
    assert filter_args[0].left.key == "id"
    assert filter_args[0].right.value == task_id
    assert filter_args[1].left.key == "user_id"
    assert filter_args[1].right.value == user_id
    db_session.query.return_value.filter.return_value.first.assert_called_once_with()


def test_task_repository_get_by_id_raises_not_found() -> None:
    # Arrange
    db_session = Mock()
    task_id = uuid.uuid4()
    db_session.query.return_value.filter.return_value.first.return_value = None
    repository = TaskRepository(db_session)

    # Act / Assert
    with pytest.raises(TaskNotFoundException, match=str(task_id)):
        repository.get_by_id(task_id, uuid.uuid4())


def test_task_repository_get_by_id_wraps_database_error() -> None:
    # Arrange
    db_session = Mock()
    db_session.query.side_effect = RuntimeError("query failed")
    repository = TaskRepository(db_session)

    # Act / Assert
    with pytest.raises(DatabaseOperationException, match="Error retrieving task"):
        repository.get_by_id(uuid.uuid4(), uuid.uuid4())


def test_task_repository_create_adds_commits_refreshes_and_returns_task() -> None:
    # Arrange
    db_session = Mock()
    task = Mock(spec=TaskModel)
    repository = TaskRepository(db_session)

    # Act
    result = repository.create(task)

    # Assert
    assert result is task
    db_session.add.assert_called_once_with(task)
    db_session.commit.assert_called_once_with()
    db_session.refresh.assert_called_once_with(task)


def test_task_repository_create_rolls_back_and_wraps_on_commit_error() -> None:
    # Arrange
    db_session = Mock()
    db_session.commit.side_effect = RuntimeError("commit failed")
    task = Mock(spec=TaskModel)
    repository = TaskRepository(db_session)

    # Act / Assert
    with pytest.raises(DatabaseOperationException, match="Error creating task"):
        repository.create(task)
    db_session.add.assert_called_once_with(task)
    db_session.rollback.assert_called_once_with()
    db_session.refresh.assert_not_called()


def test_task_repository_update_commits_refreshes_and_returns_task() -> None:
    # Arrange
    db_session = Mock()
    task = Mock(spec=TaskModel)
    repository = TaskRepository(db_session)

    # Act
    result = repository.update(task)

    # Assert
    assert result is task
    db_session.commit.assert_called_once_with()
    db_session.refresh.assert_called_once_with(task)


def test_task_repository_update_rolls_back_and_wraps_on_commit_error() -> None:
    # Arrange
    db_session = Mock()
    db_session.commit.side_effect = RuntimeError("update failed")
    task = Mock(spec=TaskModel)
    repository = TaskRepository(db_session)

    # Act / Assert
    with pytest.raises(DatabaseOperationException, match="Error updating task"):
        repository.update(task)
    db_session.rollback.assert_called_once_with()
    db_session.refresh.assert_not_called()


def test_task_repository_delete_deletes_and_commits() -> None:
    # Arrange
    db_session = Mock()
    task = Mock(spec=TaskModel)
    repository = TaskRepository(db_session)

    # Act
    result = repository.delete(task)

    # Assert
    assert result is None
    db_session.delete.assert_called_once_with(task)
    db_session.commit.assert_called_once_with()


def test_task_repository_delete_rolls_back_and_wraps_on_commit_error() -> None:
    # Arrange
    db_session = Mock()
    db_session.commit.side_effect = RuntimeError("delete failed")
    task = Mock(spec=TaskModel)
    repository = TaskRepository(db_session)

    # Act / Assert
    with pytest.raises(DatabaseOperationException, match="Error deleting task"):
        repository.delete(task)
    db_session.delete.assert_called_once_with(task)
    db_session.rollback.assert_called_once_with()


def test_user_repository_get_all_returns_users() -> None:
    # Arrange
    db_session = Mock()
    expected_users = [Mock(spec=UserModel), Mock(spec=UserModel)]
    db_session.query.return_value.all.return_value = expected_users
    repository = UserRepository(db_session)

    # Act
    result = repository.get_all()

    # Assert
    assert result == expected_users
    db_session.query.assert_called_once_with(UserModel)
    db_session.query.return_value.all.assert_called_once_with()


def test_user_repository_get_all_wraps_database_errors() -> None:
    # Arrange
    db_session = Mock()
    db_session.query.side_effect = RuntimeError("query failed")
    repository = UserRepository(db_session)

    # Act / Assert
    with pytest.raises(
        DatabaseOperationException,
        match="Error occurred while fetching users",
    ):
        repository.get_all()


def test_user_repository_get_by_id_returns_user_when_username_exists() -> None:
    # Arrange
    db_session = Mock()
    username = "test_user"
    user = Mock(spec=UserModel)
    db_session.query.return_value.filter.return_value.first.return_value = user
    repository = UserRepository(db_session)

    # Act
    result = repository.get_by_id(username)

    # Assert
    assert result is user
    db_session.query.assert_called_once_with(UserModel)
    db_session.query.return_value.filter.assert_called_once()
    filter_args = db_session.query.return_value.filter.call_args.args
    assert len(filter_args) == 1
    assert filter_args[0].left.key == "username"
    assert filter_args[0].right.value == username
    db_session.query.return_value.filter.return_value.first.assert_called_once_with()


def test_user_repository_get_by_id_raises_not_found() -> None:
    # Arrange
    db_session = Mock()
    username = "missing_user"
    db_session.query.return_value.filter.return_value.first.return_value = None
    repository = UserRepository(db_session)

    # Act / Assert
    with pytest.raises(UserNotFoundException, match=username):
        repository.get_by_id(username)


def test_user_repository_get_by_id_wraps_database_error() -> None:
    # Arrange
    db_session = Mock()
    db_session.query.side_effect = RuntimeError("query failed")
    repository = UserRepository(db_session)

    # Act / Assert
    with pytest.raises(
        DatabaseOperationException,
        match="Error occurred while fetching user with username",
    ):
        repository.get_by_id("user")


def test_user_repository_create_adds_commits_refreshes_and_returns_user() -> None:
    # Arrange
    db_session = Mock()
    user = Mock(spec=UserModel)
    repository = UserRepository(db_session)

    # Act
    result = repository.create(user)

    # Assert
    assert result is user
    db_session.add.assert_called_once_with(user)
    db_session.commit.assert_called_once_with()
    db_session.refresh.assert_called_once_with(user)


def test_user_repository_create_rolls_back_and_wraps_on_commit_error() -> None:
    # Arrange
    db_session = Mock()
    db_session.commit.side_effect = RuntimeError("commit failed")
    user = Mock(spec=UserModel)
    repository = UserRepository(db_session)

    # Act / Assert
    with pytest.raises(
        DatabaseOperationException,
        match="Error occurred while creating a new user",
    ):
        repository.create(user)
    db_session.add.assert_called_once_with(user)
    db_session.rollback.assert_called_once_with()
    db_session.refresh.assert_not_called()


def test_user_repository_update_merges_commits_refreshes_and_returns_merged_user(
) -> None:
    # Arrange
    db_session = Mock()
    user = Mock(spec=UserModel)
    merged_user = Mock(spec=UserModel)
    db_session.merge.return_value = merged_user
    repository = UserRepository(db_session)

    # Act
    result = repository.update(user)

    # Assert
    assert result is merged_user
    db_session.merge.assert_called_once_with(user)
    db_session.commit.assert_called_once_with()
    db_session.refresh.assert_called_once_with(merged_user)


def test_user_repository_update_rolls_back_and_wraps_on_commit_error() -> None:
    # Arrange
    db_session = Mock()
    db_session.merge.return_value = Mock(spec=UserModel)
    db_session.commit.side_effect = RuntimeError("update failed")
    user = Mock(spec=UserModel)
    repository = UserRepository(db_session)

    # Act / Assert
    with pytest.raises(
        DatabaseOperationException,
        match="Error occurred while updating the user",
    ):
        repository.update(user)
    db_session.merge.assert_called_once_with(user)
    db_session.rollback.assert_called_once_with()


def test_user_repository_delete_deletes_and_commits() -> None:
    # Arrange
    db_session = Mock()
    user = Mock(spec=UserModel)
    repository = UserRepository(db_session)

    # Act
    result = repository.delete(user)

    # Assert
    assert result is None
    db_session.delete.assert_called_once_with(user)
    db_session.commit.assert_called_once_with()


def test_user_repository_delete_rolls_back_and_wraps_on_commit_error() -> None:
    # Arrange
    db_session = Mock()
    db_session.commit.side_effect = RuntimeError("delete failed")
    user = Mock(spec=UserModel)
    repository = UserRepository(db_session)

    # Act / Assert
    with pytest.raises(
        DatabaseOperationException,
        match="Error occurred while deleting the user",
    ):
        repository.delete(user)
    db_session.delete.assert_called_once_with(user)
    db_session.rollback.assert_called_once_with()
