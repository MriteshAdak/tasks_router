"""Utility functions"""

from tasks_router.models.task_model import Task as TaskModel
from tasks_router.schema.task_schema import TaskResponse
from tasks_router.models.user_model import User as UserModel
from tasks_router.schema.user_schema import User as UserDTO

def convert_task_model_to_response(task: TaskModel) -> TaskResponse: # handle bad inputs
    """Convert TaskModel instance to TaskResponse schema."""

    return TaskResponse.model_validate(task)


def convert_task_models_to_responses(tasks: list[TaskModel]) -> list[TaskResponse]:
    """Convert list of TaskModel instances to list of TaskResponse schemas."""

    return [convert_task_model_to_response(task) for task in tasks]


def convert_user_model_to_user_dto_schema(user: UserModel) -> UserDTO:
    """Convert UserModel instance to UserDTO schema."""

    return UserDTO.model_validate(user)