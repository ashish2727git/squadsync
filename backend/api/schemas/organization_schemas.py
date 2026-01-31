"""
Organization Management Schemas
Pydantic schemas for organization operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class OrganizationCreateRequest(BaseModel):
    """Request to create a new organization."""
    
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Organization name cannot be empty")
        return v.strip()


class OrganizationResponse(BaseModel):
    """Organization response."""
    
    id: UUID
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}
