"""
Summon API Schemas
Pydantic schemas for Summon request/response validation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from backend.models.models import ResponseType, SummonStatus


class SummonCreateRequest(BaseModel):
    """Request schema for creating a summon."""

    squad_id: UUID = Field(..., description="UUID of the squad to summon")
    title: str = Field(..., min_length=1, max_length=255, description="Summon title")
    description: Optional[str] = Field(None, max_length=5000, description="Summon description")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration time for the summon")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty after stripping."""
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class SummonResponseUpdateRequest(BaseModel):
    """Request schema for updating a summon response."""

    response_type: ResponseType = Field(..., description="Response type: ACCEPT, DECLINE, or MAYBE")
    message: Optional[str] = Field(None, max_length=2000, description="Optional message with the response")


class UserResponseSummary(BaseModel):
    """Summary of a user's response to a summon."""

    user_id: UUID
    username: str
    response_type: ResponseType
    message: Optional[str] = None
    responded_at: datetime

    class Config:
        from_attributes = True


class SummonResponseDetail(BaseModel):
    """Detailed summon response information."""

    id: UUID
    summon_id: UUID
    user_id: UUID
    username: str
    response_type: ResponseType
    message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SummonDetail(BaseModel):
    """Detailed summon information."""

    id: UUID
    squad_id: UUID
    squad_name: str
    created_by_id: UUID
    created_by_username: str
    title: str
    description: Optional[str] = None
    status: SummonStatus
    expires_at: Optional[datetime] = None
    created_at: datetime
    total_members: int
    responses: list[SummonResponseDetail]
    response_summary: dict[str, int] = Field(
        default_factory=dict,
        description="Count of each response type: ACCEPT, DECLINE, MAYBE, PENDING",
    )

    class Config:
        from_attributes = True


class SummonListResponse(BaseModel):
    """List of summons with pagination."""

    summons: list[SummonDetail]
    total: int
    page: int
    page_size: int


class SummonNotification(BaseModel):
    """Real-time notification payload for summon events."""

    event_type: str = Field(..., description="Event type: summon_created, response_updated, summon_expired")
    summon_id: UUID
    squad_id: UUID
    data: dict = Field(default_factory=dict, description="Event-specific data")


class SummonResponseNotification(BaseModel):
    """Real-time notification for summon response updates."""

    event_type: str = Field(default="summon_response_updated")
    summon_id: UUID
    user_id: UUID
    username: str
    response_type: ResponseType
    message: Optional[str] = None
    response_count: dict[str, int] = Field(..., description="Current count of each response type")
