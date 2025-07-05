from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class StatusType(str, Enum):
    """Enum for status."""
    DONE = "done"
    IN_PROGRESS = "in_progress"
    NOT_ACTIVATE = "not_activate"


class NoteCreate(BaseModel):
    """Schema for creating note."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    comment: Optional[str] = None
    status: StatusType = Field(default=StatusType.IN_PROGRESS)


class NoteUpdate(BaseModel):
    """Schema for the updating note."""
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    comment: Optional[str] = None
    status: Optional[StatusType] = None


class NoteResponse(BaseModel):
    """Schema for getting note."""
    id: int
    name: str
    description: Optional[str]
    comment: Optional[str]
    status: StatusType

    class Config:
        from_attributes = True
