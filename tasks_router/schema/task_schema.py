"""
Schema definitions for task-related operations
"""

import uuid

from pydantic import BaseModel, Field, AliasChoices, ConfigDict
from datetime import datetime

from tasks_router.enums.task_statuses import TaskStatus

class TaskCreate(BaseModel):
    """Request schema for creating a new task.

    Attributes:
        title (str): The title of the task.
        status (TaskStatus): The initial status of the task.
        due_date (datetime | None): Optional due date for the task. Supports aliases 'dueDate' and 'due_date'.
    """

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
    """Request schema for updating an existing task.

    Attributes:
        title (str | None): Updated title for the task.
        status (TaskStatus | None): Updated task status.
        due_date (datetime | None): Optional updated due date. Supports aliases 'dueDate' and 'due_date'.
    """

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
    """Response schema for task objects returned by the API.

    Attributes:
        id (uuid.UUID): Unique identifier for the task.
        title (str): The title of the task.
        status (TaskStatus): Current status of the task.
        due_date (datetime | None): Optional due date for the task.
    """
    id: uuid.UUID
    title: str
    status: TaskStatus
    due_date: datetime | None
    # add audit fields if and when needed
    model_config = ConfigDict(from_attributes=True)