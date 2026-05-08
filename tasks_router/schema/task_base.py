"""
Schema definitions for task-related operations
"""

from pydantic import BaseModel, Field, AliasChoices
from datetime import datetime

class Task(BaseModel):
    title: str
    status: str = 'todo'
    due_date: datetime | None = Field(default=None, validation_alias=AliasChoices('dueDate', 'due_date'))
    