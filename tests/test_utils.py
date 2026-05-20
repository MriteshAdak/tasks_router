import uuid
from datetime import UTC, datetime

from tasks_router.enums.task_statuses import TaskStatus
from tasks_router.models.task_model import Task
from tasks_router.models.user_model import User as UserModel
from tasks_router.schema.task_schema import TaskCreate
from tasks_router.utils import (
    convert_task_model_to_response_dto,
    convert_task_models_to_responses_dto,
    convert_task_schema_dto_to_task_model,
    convert_user_model_to_user_schema_dto,
)


def test_convert_task_model_to_response_dto() -> None:
    task = Task(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="Write tests",
        status=TaskStatus.TODO,
        due_date=datetime.now(UTC),
    )

    response = convert_task_model_to_response_dto(task)

    assert response.id == task.id
    assert response.title == "Write tests"
    assert response.status == TaskStatus.TODO


def test_convert_task_models_to_responses_dto() -> None:
    task_1 = Task(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="Task 1",
        status=TaskStatus.TODO,
        due_date=None,
    )
    task_2 = Task(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="Task 2",
        status=TaskStatus.DONE,
        due_date=None,
    )

    response = convert_task_models_to_responses_dto([task_1, task_2])

    assert [item.id for item in response] == [task_1.id, task_2.id]
    assert [item.status for item in response] == [TaskStatus.TODO, TaskStatus.DONE]


def test_convert_user_model_to_user_schema_dto() -> None:
    user = UserModel(
        id=uuid.uuid4(),
        username="mritesh",
        display_name="Mritesh Adak",
    )

    response = convert_user_model_to_user_schema_dto(user)

    assert response.id == user.id
    assert response.username == user.username
    assert response.display_name == user.display_name


def test_convert_task_schema_dto_to_task_model() -> None:
    due_date = datetime.now(UTC)
    task_create = TaskCreate(
        title="Draft tests",
        status=TaskStatus.IN_PROGRESS,
        due_date=due_date,
    )

    task_model = convert_task_schema_dto_to_task_model(task_create)

    assert task_model.title == "Draft tests"
    assert task_model.status == TaskStatus.IN_PROGRESS
    assert task_model.due_date == due_date
