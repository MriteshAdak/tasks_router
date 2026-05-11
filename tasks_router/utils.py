"""Utility functions"""

from tasks_router.models.task_model import Task as TaskModel
from tasks_router.schema.task_response import TaskResponse
from tasks_router.models.user_model import User as UserModel
from tasks_router.schema.user_schema import User as UserDTO

def convert_task_model_to_response(task: TaskModel) -> TaskResponse: # handle bad inputs
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


def convert_user_model_to_user_dto_schema(user: UserModel) -> UserDTO:
    """Convert UserModel instance to UserDTO schema."""

    return UserDTO(
        username=user.username,
        display_name=user.display_name
    )