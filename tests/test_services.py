import uuid

import pytest

from tasks_router.enums.task_statuses import TaskStatus
from tasks_router.exceptions.custom_exceptions import TaskNotFoundException, UserNotFoundException
from tasks_router.models.task_model import Task as TaskModel
from tasks_router.models.user_model import User as UserModel
from tasks_router.schema.task_schema import TaskCreate, TaskUpdate
from tasks_router.schema.user_schema import User as UserSchema
from tasks_router.services.task_service import TaskServices
from tasks_router.services.user_service import UserService


class FakeTaskRepository:
    def __init__(self, tasks=None):
        self.tasks = {t.id: t for t in (tasks or [])}

    def get_all(self, user_id):
        return [t for t in self.tasks.values() if t.user_id == user_id]

    def create(self, task):
        if not task.id:
            task.id = uuid.uuid4()
        self.tasks[task.id] = task
        return task

    def get_by_id(self, task_id, user_id):
        task = self.tasks.get(task_id)
        if task and task.user_id == user_id:
            return task
        raise TaskNotFoundException(task_id)

    def update(self, task):
        self.tasks[task.id] = task
        return task

    def delete(self, task):
        if task.id in self.tasks:
            del self.tasks[task.id]


class FakeUserRepository:
    def __init__(self, users=None):
        self.users = {u.username: u for u in (users or [])}

    def get_by_username(self, username):
        user = self.users.get(username)
        if not user:
            raise UserNotFoundException(username)
        return user

    def create(self, user):
        self.users[user.username] = user
        return user


@pytest.mark.unit
def test_task_services_get_all_empty():
    repo = FakeTaskRepository()
    service = TaskServices(repo)

    result = service.get_all(uuid.uuid4())

    assert result == []


@pytest.mark.unit
def test_task_services_get_all_with_data():
    user_id = uuid.uuid4()
    task = TaskModel(id=uuid.uuid4(), user_id=user_id, title="Task 1", status=TaskStatus.TODO)
    repo = FakeTaskRepository(tasks=[task])
    service = TaskServices(repo)

    result = service.get_all(user_id)

    assert len(result) == 1
    assert result[0].title == "Task 1"


@pytest.mark.unit
def test_task_services_create_returns_response():
    repo = FakeTaskRepository()
    service = TaskServices(repo)
    user_id = uuid.uuid4()
    payload = TaskCreate(title="Plan sprint", status=TaskStatus.TODO)

    response = service.create(payload, user_id)

    assert len(repo.tasks) == 1
    created_task = list(repo.tasks.values())[0]
    assert created_task.user_id == user_id
    assert response.title == "Plan sprint"


@pytest.mark.unit
def test_task_services_update_updates_fields():
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    existing = TaskModel(
        id=task_id,
        user_id=user_id,
        title="Draft",
        status=TaskStatus.TODO,
        due_date=None,
    )
    repo = FakeTaskRepository(tasks=[existing])
    service = TaskServices(repo)

    response = service.update(task_id, user_id, TaskUpdate(title="Final", status=TaskStatus.DONE))

    assert response.title == "Final"
    assert response.status == TaskStatus.DONE
    assert repo.tasks[task_id].title == "Final"


@pytest.mark.unit
def test_task_services_update_not_found_raises():
    repo = FakeTaskRepository()
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
    repo = FakeUserRepository(users=[user_model])
    service = UserService(repo)

    response = service.get_user("bob")

    assert response.username == "bob"
    assert response.display_name == "Bob Example"


@pytest.mark.unit
def test_user_service_get_user_not_found():
    repo = FakeUserRepository()
    service = UserService(repo)

    with pytest.raises(UserNotFoundException):
        service.get_user("missing")


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

    assert "carol" in repo.users
    assert response.username == "carol"
