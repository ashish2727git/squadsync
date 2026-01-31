"""
Team Management Schemas
Pydantic schemas for team operations.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TeamCreateRequest(BaseModel):
    """Request to create a new team."""
    
    name: str = Field(..., min_length=2, max_length=100)
    game_title: str = Field(..., min_length=2, max_length=100)
    organization_id: UUID
    
    @field_validator("name", "game_title")
    @classmethod
    def validate_strings(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class TeamResponse(BaseModel):
    """Team response."""
    
    id: UUID
    name: str
    game_title: str
    organization_id: UUID
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}
