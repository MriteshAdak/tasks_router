"""
TaskModel for SQLAlchemy ORM, representing the 'task' table in the database.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, UUID, ForeignKey
# from sqlalchemy.sql import func

from tasks_router.database.initiate_db import Base
from tasks_router.enums.task_statuses import TaskStatus

class Task(Base):
    __tablename__ = 'task'
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        default=uuid.uuid4,
        primary_key=True
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey('user.id', ondelete='CASCADE'),
        index=True,
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    
    status: Mapped[TaskStatus] = mapped_column(
        String,
        default=TaskStatus.TODO,
        nullable=False
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # For auditing purposes only, not exposed in API responses

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(UTC),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
        nullable=False
    )