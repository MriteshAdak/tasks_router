"""Utility functions"""

from tasks_router.models.task_model import Task as TaskModel
from tasks_router.schema.task_response import TaskResponse


def convert_task_model_to_response(task: TaskModel) -> TaskResponse:
    """Convert TaskModel instance to TaskResponse schema."""

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        status=task.status,
        due_date=task.due_date
    )


def convert_task_models_to_responses(tasks: list[TaskModel]) -> list[TaskResponse]:
    """Convert list of TaskModel instances to list of TaskResponse schemas."""

    return [convert_task_model_to_response(task) for task in tasks]
