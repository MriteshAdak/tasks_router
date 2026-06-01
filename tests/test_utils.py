import uuid
from datetime import UTC, datetime

import pytest

from tasks_router.enums.task_statuses import TaskStatus
from tasks_router.models.task_model import Task as TaskModel
from tasks_router.models.user_model import User as UserModel
from tasks_router.schema.task_schema import TaskCreate
from tasks_router.utils import (
	convert_task_model_to_response_dto,
	convert_task_models_to_responses_dto,
	convert_task_schema_dto_to_task_model,
	convert_user_model_to_user_schema_dto,
)


@pytest.mark.unit
def test_convert_task_model_to_response_dto():
	task_id = uuid.uuid4()
	user_id = uuid.uuid4()
	due_date = datetime.now(UTC)
	task = TaskModel(
		id=task_id,
		user_id=user_id,
		title="Write tests",
		status=TaskStatus.IN_PROGRESS,
		due_date=due_date,
	)

	response = convert_task_model_to_response_dto(task)

	assert response.id == task_id
	assert response.title == "Write tests"
	assert response.status == TaskStatus.IN_PROGRESS
	assert response.due_date == due_date


@pytest.mark.unit
def test_convert_task_models_to_responses_dto():
	task_id = uuid.uuid4()
	task = TaskModel(
		id=task_id,
		user_id=uuid.uuid4(),
		title="Prepare release",
		status=TaskStatus.TODO,
		due_date=None,
	)

	responses = convert_task_models_to_responses_dto([task])

	assert len(responses) == 1
	assert responses[0].id == task_id


@pytest.mark.unit
def test_convert_user_model_to_user_schema_dto():
	user_id = uuid.uuid4()
	user = UserModel(
		id=user_id,
		username="alice",
		display_name="Alice Example",
	)

	response = convert_user_model_to_user_schema_dto(user)

	assert response.id == user_id
	assert response.username == "alice"
	assert response.display_name == "Alice Example"


@pytest.mark.unit
def test_convert_task_schema_dto_to_task_model():
	due_date = datetime.now(UTC)
	payload = TaskCreate(
		title="Follow up",
		status=TaskStatus.DONE,
		due_date=due_date,
	)

	model = convert_task_schema_dto_to_task_model(payload)

	assert model.title == "Follow up"
	assert model.status == TaskStatus.DONE
	assert model.due_date == due_date
