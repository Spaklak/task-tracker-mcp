from enum import Enum

class StatusType(str, Enum):
    """Enum for status."""
    DONE = "done"
    IN_PROGRESS = "in_progress"
    NOT_ACTIVATE = "not_activate"