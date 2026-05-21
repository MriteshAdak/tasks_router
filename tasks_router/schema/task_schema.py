"""
Schema definitions for task-related operations.
"""

import uuid

from pydantic import BaseModel, Field, AliasChoices, ConfigDict
from datetime import datetime

from tasks_router.enums.task_statuses import TaskStatus

class TaskCreate(BaseModel):
    """Input schema for creating a task."""

    title: str
    status: TaskStatus = TaskStatus.TODO
    due_date: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices(
            'dueDate',
            'due_date'
        )
    )
    model_config = ConfigDict(from_attributes=True)

class TaskUpdate(BaseModel):
    """Input schema for updating a task."""

    title: str | None = None
    status: TaskStatus | None = None
    due_date: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices(
            'dueDate',
            'due_date'
        )
    )
    model_config = ConfigDict(from_attributes=True)

class TaskResponse(BaseModel):
    """Response schema returned for task resources."""

    id: uuid.UUID
    title: str
    status: TaskStatus
    due_date: datetime | None
    # Audit fields are omitted until API contracts require them.
    model_config = ConfigDict(from_attributes=True)
