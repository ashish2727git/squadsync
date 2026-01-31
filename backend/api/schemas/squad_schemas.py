"""
Squad Management Schemas
Pydantic schemas for squad CRUD operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SquadCreateRequest(BaseModel):
    """Request to create a new squad."""
    
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    team_id: UUID
    max_members: Optional[int] = Field(10, ge=2, le=50)
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Squad name cannot be empty")
        return v.strip()


class SquadResponse(BaseModel):
    """Squad summary response."""
    
    id: UUID
    name: str
    description: Optional[str]
    team_id: UUID
    max_members: int
    member_count: int
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class SquadMemberResponse(BaseModel):
    """Squad member information."""
    
    id: UUID
    username: str
    is_leader: bool = False


class SquadDetailResponse(BaseModel):
    """Detailed squad information with members."""
    
    id: UUID
    name: str
    description: Optional[str]
    team_id: UUID
    max_members: int
    member_count: int
    is_active: bool
    created_at: datetime
    members: List[SquadMemberResponse]
    
    model_config = {"from_attributes": True}


class SquadJoinRequest(BaseModel):
    """Request to join a squad."""
    
    invite_code: Optional[str] = None


class QuickSquadCreateRequest(BaseModel):
    """Quick create - creates org, team, and squad in one step."""
    
    squad_name: str = Field(..., min_length=2, max_length=100)
    squad_description: Optional[str] = Field(None, max_length=500)
    game_title: str = Field("General", max_length=100)
    max_members: Optional[int] = Field(10, ge=2, le=50)
    
    @field_validator("squad_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Squad name cannot be empty")
        return v.strip()
