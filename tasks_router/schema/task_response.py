from tasks_router.schema.task_base import Task


class TaskResponse(Task):
    id: str
    # user_id: str