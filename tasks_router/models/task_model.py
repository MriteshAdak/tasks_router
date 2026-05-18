"""
TaskModel for SQLAlchemy ORM, representing the 'task' table in the database.
"""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, UUID, ForeignKey

from tasks_router.database.initiate_db import Base

class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class Task(Base):
    __tablename__ = 'task'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('user.id', ondelete='CASCADE'), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(String, default=TaskStatus.TODO, nullable=False)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)