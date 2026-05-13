"""
TaskModel for SQLAlchemy ORM, representing the 'task' table in the database.
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, UUID, ForeignKey

from tasks_router.database.initiate_db import Base

class Task(Base):
    __tablename__ = 'task'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('user.id'), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default='todo', nullable=False)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)