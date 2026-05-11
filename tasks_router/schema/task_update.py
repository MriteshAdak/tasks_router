from tasks_router.schema.task_base import Task

class TaskUpdate(Task):
    id: str
    # user_id: str