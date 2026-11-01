from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

VALID_PRIORITIES = {"low", "medium", "high", "critical"}
VALID_STATUSES = {"pending", "in_progress", "completed", "blocked"}

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: datetime
    priority: str = Field(default="medium")
    status: str = Field(default="pending")
    dependency_id: Optional[str] = None

    @field_validator("priority")
    @classmethod
    def val_priority(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of {list(VALID_PRIORITIES)}")
        return clean

    @field_validator("status")
    @classmethod
    def val_status(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean not in VALID_STATUSES:
            raise ValueError(f"Status must be one of {list(VALID_STATUSES)}")
        return clean

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    dependency_id: Optional[str] = None

