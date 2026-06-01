import uuid

import pytest

from tasks_router.enums.task_statuses import TaskStatus
from tasks_router.exceptions.custom_exceptions import TaskNotFoundException, UserNotFoundException
from tasks_router.models.task_model import Task as TaskModel
from tasks_router.models.user_model import User as UserModel
from tasks_router.repositories.task_repo import TaskRepository
from tasks_router.repositories.user_repo import UserRepository


@pytest.mark.integration
def test_user_repository_create_and_get(db_session):
	repo = UserRepository(db_session)
	user = UserModel(
		id=uuid.uuid4(),
		username="alice",
		display_name="Alice Example",
	)

	created = repo.create(user)
	fetched = repo.get_by_username("alice")

	assert fetched.id == created.id
	assert fetched.display_name == "Alice Example"


@pytest.mark.integration
def test_user_repository_get_missing_raises(db_session):
	repo = UserRepository(db_session)

	with pytest.raises(UserNotFoundException):
		repo.get_by_username("missing")


@pytest.mark.integration
def test_task_repository_crud(db_session):
	user = UserModel(
		id=uuid.uuid4(),
		username="owner",
		display_name="Owner",
	)
	db_session.add(user)
	db_session.commit()

	repo = TaskRepository(db_session)
	task = TaskModel(
		id=uuid.uuid4(),
		user_id=user.id,
		title="Initial",
		status=TaskStatus.TODO,
		due_date=None,
	)

	created = repo.create(task)
	fetched = repo.get_by_id(created.id, user.id)

	assert fetched.title == "Initial"

	fetched.title = "Updated"
	updated = repo.update(fetched)

	assert updated.title == "Updated"

	all_tasks = repo.get_all(user.id)

	assert len(all_tasks) == 1

	repo.delete(updated)

	assert repo.get_all(user.id) == []


@pytest.mark.integration
def test_task_repository_get_missing_raises(db_session):
	repo = TaskRepository(db_session)

	with pytest.raises(TaskNotFoundException):
		repo.get_by_id(uuid.uuid4(), uuid.uuid4())
