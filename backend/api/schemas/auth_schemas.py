"""
Authentication API Schemas
Pydantic schemas for authentication request/response validation.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from backend.core.security import sanitize_email, sanitize_username, validate_password_strength


class UserRegisterRequest(BaseModel):
    """Request schema for user registration."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    role: Optional[str] = Field(
        default="PLAYER",
        description="User role (defaults to PLAYER, only admins can set other roles)",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate and sanitize username."""
        return sanitize_username(v)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate and sanitize email."""
        return sanitize_email(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        """Validate user role."""
        if v is None:
            return "PLAYER"
        
        allowed_roles = {"ORG_ADMIN", "TEAM_MANAGER", "SQUAD_LEADER", "PLAYER"}
        v_upper = v.upper()
        if v_upper not in allowed_roles:
            raise ValueError(f"Role must be one of {allowed_roles}")
        return v_upper


class UserLoginRequest(BaseModel):
    """Request schema for user login."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Sanitize username/email input."""
        return v.strip()


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""

    access_token: str = Field(..., description="JWT access token (short-lived)")
    refresh_token: str = Field(..., description="JWT refresh token (long-lived)")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str = Field(..., description="JWT refresh token")


class UserResponse(BaseModel):
    """Response schema for user information."""

    id: UUID = Field(..., description="User UUID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether user account is active")
    is_verified: bool = Field(..., description="Whether user email is verified")

    class Config:
        from_attributes = True
