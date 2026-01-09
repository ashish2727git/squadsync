"""
Player Vault API Schemas
Pydantic schemas for vault request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class VaultDataUpdateRequest(BaseModel):
    """Request schema for updating vault data."""

    data: Dict[str, Any] = Field(
        ...,
        description="Vault data as JSON object",
        examples=[{"stats": {"level": 10, "xp": 5000}, "inventory": []}],
    )

    @field_validator("data")
    @classmethod
    def validate_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate vault data structure and size."""
        if not isinstance(v, dict):
            raise ValueError("Vault data must be a JSON object")

        # Check maximum depth (prevent deeply nested structures)
        def check_depth(obj: Any, depth: int = 0, max_depth: int = 10) -> None:
            if depth > max_depth:
                raise ValueError(f"Vault data exceeds maximum nesting depth of {max_depth}")
            if isinstance(obj, dict):
                for value in obj.values():
                    check_depth(value, depth + 1, max_depth)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, depth + 1, max_depth)

        check_depth(v)

        # Check approximate size (rough estimate)
        import json

        data_str = json.dumps(v)
        max_size = 1024 * 1024  # 1MB limit
        if len(data_str) > max_size:
            raise ValueError(f"Vault data exceeds maximum size of {max_size} bytes")

        return v


class VaultDataMergeRequest(BaseModel):
    """Request schema for merging vault data (partial update)."""

    data: Dict[str, Any] = Field(
        ...,
        description="Vault data to merge with existing data",
        examples=[{"stats": {"level": 11}}],
    )

    @field_validator("data")
    @classmethod
    def validate_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate merge data structure."""
        if not isinstance(v, dict):
            raise ValueError("Vault data must be a JSON object")

        # Check maximum depth
        def check_depth(obj: Any, depth: int = 0, max_depth: int = 10) -> None:
            if depth > max_depth:
                raise ValueError(f"Vault data exceeds maximum nesting depth of {max_depth}")
            if isinstance(obj, dict):
                for value in obj.values():
                    check_depth(value, depth + 1, max_depth)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, depth + 1, max_depth)

        check_depth(v)

        return v


class VaultShareRequest(BaseModel):
    """Request schema for sharing vault data to chat."""

    target_id: UUID = Field(..., description="Target chat/squad/room ID to share to")
    target_type: str = Field(
        ...,
        description="Target type: 'squad', 'team', or 'chat'",
        pattern="^(squad|team|chat)$",
    )
    data_keys: Optional[list[str]] = Field(
        None,
        description="Specific keys to share (if None, shares all data)",
        max_length=50,
    )
    message: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional message to accompany shared data",
    )

    @field_validator("target_type")
    @classmethod
    def validate_target_type(cls, v: str) -> str:
        """Validate target type."""
        allowed_types = {"squad", "team", "chat"}
        if v not in allowed_types:
            raise ValueError(f"target_type must be one of {allowed_types}")
        return v

    @field_validator("data_keys")
    @classmethod
    def validate_data_keys(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate data keys."""
        if v is not None:
            if len(v) == 0:
                raise ValueError("data_keys cannot be empty list")
            if len(v) > 50:
                raise ValueError("data_keys cannot exceed 50 items")
            # Validate key format (alphanumeric, underscore, dot)
            for key in v:
                if not isinstance(key, str):
                    raise ValueError("All data_keys must be strings")
                if len(key) > 100:
                    raise ValueError("Data key names cannot exceed 100 characters")
        return v


class VaultDetail(BaseModel):
    """Vault detail response schema."""

    id: UUID
    user_id: UUID
    vault_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VaultShareResponse(BaseModel):
    """Response schema for vault share operation."""

    success: bool
    message: str
    shared_at: datetime
    target_type: str
    target_id: UUID
    data_keys_shared: Optional[list[str]] = None


class VaultAuditLog(BaseModel):
    """Vault audit log entry."""

    id: UUID
    vault_id: UUID
    user_id: UUID
    action: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
