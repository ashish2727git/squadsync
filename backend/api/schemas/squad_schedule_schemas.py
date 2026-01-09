"""
Squad Schedule API Schemas
Pydantic schemas for squad events and daily goals.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class SquadEventCreateRequest(BaseModel):
    """Request schema for creating a squad event."""

    squad_id: UUID = Field(..., description="UUID of the squad")
    title: str = Field(..., min_length=1, max_length=255, description="Event title")
    description: Optional[str] = Field(None, max_length=5000, description="Event description")
    start_time: datetime = Field(..., description="Event start time (timezone-aware)")
    end_time: Optional[datetime] = Field(None, description="Event end time (timezone-aware)")
    event_type: str = Field(
        default="general",
        description="Event type: practice, match, meeting, general",
        max_length=50,
    )
    location: Optional[str] = Field(None, max_length=255, description="Event location")
    is_all_day: bool = Field(default=False, description="Whether event is all-day")
    is_recurring: bool = Field(default=False, description="Whether event is recurring")
    recurrence_pattern: Optional[str] = Field(
        None,
        max_length=100,
        description="Recurrence pattern: daily, weekly, monthly",
    )
    metadata: dict = Field(default_factory=dict, description="Additional metadata for analytics")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty after stripping."""
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        """Validate event type."""
        allowed_types = {"practice", "match", "meeting", "general"}
        if v not in allowed_types:
            raise ValueError(f"event_type must be one of {allowed_types}")
        return v

    @field_validator("recurrence_pattern")
    @classmethod
    def validate_recurrence_pattern(cls, v: Optional[str]) -> Optional[str]:
        """Validate recurrence pattern."""
        if v is not None:
            allowed_patterns = {"daily", "weekly", "monthly"}
            if v not in allowed_patterns:
                raise ValueError(f"recurrence_pattern must be one of {allowed_patterns}")
        return v

    @model_validator(mode="after")
    def validate_times(self) -> "SquadEventCreateRequest":
        """Validate start and end times."""
        if self.end_time and self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        if self.is_recurring and not self.recurrence_pattern:
            raise ValueError("recurrence_pattern is required when is_recurring is True")
        return self


class SquadEventUpdateRequest(BaseModel):
    """Request schema for updating a squad event."""

    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Event title")
    description: Optional[str] = Field(None, max_length=5000, description="Event description")
    start_time: Optional[datetime] = Field(None, description="Event start time")
    end_time: Optional[datetime] = Field(None, description="Event end time")
    event_type: Optional[str] = Field(
        None,
        description="Event type: practice, match, meeting, general",
        max_length=50,
    )
    location: Optional[str] = Field(None, max_length=255, description="Event location")
    is_all_day: Optional[bool] = Field(None, description="Whether event is all-day")
    is_recurring: Optional[bool] = Field(None, description="Whether event is recurring")
    recurrence_pattern: Optional[str] = Field(
        None,
        max_length=100,
        description="Recurrence pattern: daily, weekly, monthly",
    )
    metadata: Optional[dict] = Field(None, description="Additional metadata")
    is_active: Optional[bool] = Field(None, description="Whether event is active")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title if provided."""
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip() if v else None

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate event type if provided."""
        if v is not None:
            allowed_types = {"practice", "match", "meeting", "general"}
            if v not in allowed_types:
                raise ValueError(f"event_type must be one of {allowed_types}")
        return v

    @model_validator(mode="after")
    def validate_times(self) -> "SquadEventUpdateRequest":
        """Validate start and end times."""
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        if self.is_recurring and not self.recurrence_pattern:
            raise ValueError("recurrence_pattern is required when is_recurring is True")
        return self


class SquadEventDetail(BaseModel):
    """Detailed squad event information."""

    id: UUID
    squad_id: UUID
    squad_name: str
    created_by_id: Optional[UUID]
    created_by_username: Optional[str]
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    event_type: str
    location: Optional[str]
    is_all_day: bool
    is_recurring: bool
    recurrence_pattern: Optional[str]
    metadata: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SquadEventListResponse(BaseModel):
    """List of squad events with pagination."""

    events: list[SquadEventDetail]
    total: int
    page: int
    page_size: int


class SquadDailyGoalCreateRequest(BaseModel):
    """Request schema for creating/updating a squad daily goal."""

    squad_id: UUID = Field(..., description="UUID of the squad")
    goal_text: str = Field(..., min_length=1, max_length=2000, description="Goal text")
    target_date: datetime = Field(..., description="Date this goal is for (timezone-aware)")
    metadata: dict = Field(default_factory=dict, description="Additional metadata for analytics")

    @field_validator("goal_text")
    @classmethod
    def validate_goal_text(cls, v: str) -> str:
        """Validate goal text is not empty after stripping."""
        if not v.strip():
            raise ValueError("Goal text cannot be empty")
        return v.strip()


class SquadDailyGoalUpdateRequest(BaseModel):
    """Request schema for updating a squad daily goal."""

    goal_text: Optional[str] = Field(None, min_length=1, max_length=2000, description="Goal text")
    is_completed: Optional[bool] = Field(None, description="Whether goal is completed")
    metadata: Optional[dict] = Field(None, description="Additional metadata")

    @field_validator("goal_text")
    @classmethod
    def validate_goal_text(cls, v: Optional[str]) -> Optional[str]:
        """Validate goal text if provided."""
        if v is not None and not v.strip():
            raise ValueError("Goal text cannot be empty")
        return v.strip() if v else None


class SquadDailyGoalDetail(BaseModel):
    """Detailed squad daily goal information."""

    id: UUID
    squad_id: UUID
    squad_name: str
    created_by_id: Optional[UUID]
    created_by_username: Optional[str]
    goal_text: str
    target_date: datetime
    is_completed: bool
    completed_at: Optional[datetime]
    completed_by_id: Optional[UUID]
    completed_by_username: Optional[str]
    metadata: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SquadScheduleDashboard(BaseModel):
    """Dashboard view with upcoming events and current daily goal."""

    squad_id: UUID
    squad_name: str
    upcoming_events: list[SquadEventDetail]
    current_goal: Optional[SquadDailyGoalDetail]
    event_count: int
    goal_completion_rate: Optional[float] = Field(
        None, description="Goal completion rate (for analytics)"
    )
