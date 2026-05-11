import uuid
from typing import List

from sqlalchemy.orm import Session

# from tasks_router.database import engine
from tasks_router.models.task_model import Task as TaskModel
from tasks_router.schema.task_base import Task as TaskSchema

class TaskServices:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def get(self, user_id: str) -> List[TaskModel]:
        return self.db_session.query(TaskModel).filter(TaskModel.user_id == user_id).all()
    
    def create(self, task: TaskSchema) -> TaskModel:
        new_task = TaskModel(
            id=str(uuid.uuid4()),
            user_id=task.user_id,
            title=task.title,
            status=task.status,
            due_date=task.due_date if task.due_date else None
        )
        self.db_session.add(new_task)
        self.db_session.commit()
        self.db_session.refresh(new_task)
        return new_task
    
    def update(self, task_id: str, task: TaskSchema) -> TaskModel | None:
        existing_task = self.db_session.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not existing_task:
            return None
        existing_task.title = task.title
        existing_task.status = task.status
        existing_task.due_date = task.due_date if task.due_date else None
        self.db_session.commit()
        self.db_session.refresh(existing_task)
        return existing_task
    
    def delete(self, task_id: str) -> bool:
        existing_task = self.db_session.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not existing_task:
            return False
        self.db_session.delete(existing_task)
        self.db_session.commit()
        return True