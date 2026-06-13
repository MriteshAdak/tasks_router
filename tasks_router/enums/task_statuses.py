from enum import StrEnum

class TaskStatus(StrEnum):
    """Enumerated task states used by the task API and persistence layer."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
