import uuid

import pytest

from tasks_router.enums.task_statuses import TaskStatus
from tasks_router.exceptions.custom_exceptions import TaskNotFoundException
from tasks_router.models.task_model import Task as TaskModel
from tasks_router.models.user_model import User as UserModel
from tasks_router.schema.task_schema import TaskCreate, TaskUpdate
from tasks_router.schema.user_schema import User as UserSchema
from tasks_router.services.task_service import TaskServices
from tasks_router.services.user_service import UserService


class FakeTaskRepository:
	def __init__(self, tasks=None):
		self.tasks = tasks or []
		self.created = None
		self.updated = None
		self.deleted = None
		self.task_by_id = None
		self.raise_not_found = False

	def get_all(self, user_id):
		return self.tasks

	def create(self, task):
		self.created = task
		return task

	def get_by_id(self, task_id, user_id):
		if self.raise_not_found:
			raise TaskNotFoundException(task_id)
		if self.task_by_id is not None:
			return self.task_by_id
		raise TaskNotFoundException(task_id)

	def update(self, task):
		self.updated = task
		return task

	def delete(self, task):
		self.deleted = task


class FakeUserRepository:
	def __init__(self, user=None):
		self.user = user
		self.created = None

	def get_by_username(self, username):
		if self.user is None:
			raise Exception("missing user")
		return self.user

	def create(self, user):
		self.created = user
		return user


@pytest.mark.unit
def test_task_services_get_all_empty():
	repo = FakeTaskRepository(tasks=[])
	service = TaskServices(repo)

	result = service.get_all(uuid.uuid4())

	assert result == []


@pytest.mark.unit
def test_task_services_create_returns_response():
	repo = FakeTaskRepository()
	service = TaskServices(repo)
	user_id = uuid.uuid4()
	payload = TaskCreate(title="Plan sprint", status=TaskStatus.TODO)

	response = service.create(payload, user_id)

	assert repo.created is not None
	assert repo.created.user_id == user_id
	assert response.title == "Plan sprint"


@pytest.mark.unit
def test_task_services_update_updates_fields():
	repo = FakeTaskRepository()
	service = TaskServices(repo)
	task_id = uuid.uuid4()
	user_id = uuid.uuid4()
	existing = TaskModel(
		id=task_id,
		user_id=user_id,
		title="Draft",
		status=TaskStatus.TODO,
		due_date=None,
	)
	repo.task_by_id = existing

	response = service.update(task_id, user_id, TaskUpdate(title="Final"))

	assert repo.updated is existing
	assert response.title == "Final"


@pytest.mark.unit
def test_task_services_update_not_found_raises():
	repo = FakeTaskRepository()
	repo.raise_not_found = True
	service = TaskServices(repo)

	with pytest.raises(TaskNotFoundException):
		service.update(uuid.uuid4(), uuid.uuid4(), TaskUpdate(title="Missing"))


@pytest.mark.unit
def test_user_service_get_user():
	user_model = UserModel(
		id=uuid.uuid4(),
		username="bob",
		display_name="Bob Example",
	)
	repo = FakeUserRepository(user=user_model)
	service = UserService(repo)

	response = service.get_user("bob")

	assert response.username == "bob"
	assert response.display_name == "Bob Example"


@pytest.mark.unit
def test_user_service_create():
	repo = FakeUserRepository()
	service = UserService(repo)
	payload = UserSchema(
		id=uuid.uuid4(),
		username="carol",
		display_name="Carol Example",
	)

	response = service.create(payload)

	assert repo.created is not None
	assert response.username == "carol"
