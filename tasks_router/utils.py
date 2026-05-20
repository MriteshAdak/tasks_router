"""Utility conversion helpers between ORM models and API DTOs."""

from tasks_router.models.task_model import Task as TaskModel
from tasks_router.schema.task_schema import TaskCreate, TaskResponse
from tasks_router.models.user_model import User as UserModel
from tasks_router.schema.user_schema import User as UserDTO

def convert_task_model_to_response_dto(task: TaskModel) -> TaskResponse:
    """Convert a task model to a response DTO.

    Args:
        task: Persisted task model.

    Returns:
        Task response DTO for API serialization.
    """

    return TaskResponse.model_validate(task)


def convert_task_models_to_responses_dto(tasks: list[TaskModel]) -> list[TaskResponse]:
    """Convert task models to response DTOs.

    Args:
        tasks: Persisted task models.

    Returns:
        Task response DTO list for API serialization.
    """

    return [convert_task_model_to_response_dto(task) for task in tasks]


def convert_user_model_to_user_schema_dto(user: UserModel) -> UserDTO:
    """Convert a user model to an API DTO.

    Args:
        user: Persisted user model.

    Returns:
        User DTO for API serialization.
    """

    return UserDTO.model_validate(user)


# Conversion is retained for future create-task paths that still accept
# schema DTO inputs before full service-level validation is introduced.
def convert_task_schema_dto_to_task_model(task: TaskCreate) -> TaskModel:
    """Convert a task create DTO to a task model.

    Args:
        task: Task create DTO from API payload.

    Returns:
        Unsaved task model for repository persistence.
    """

    return TaskModel(
        # user_id=task.user_id,
        title=task.title,
        status=task.status,
        due_date=task.due_date if task.due_date else None
    )
