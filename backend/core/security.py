"""
Security Utilities
Production-grade password hashing and security functions.
"""

import re
from typing import Optional

import bcrypt
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with passlib.

    Args:
        password: Plain text password

    Returns:
        Hashed password string

    Raises:
        ValueError: If password is empty or None
    """
    # bcrypt limit safeguard
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password too long (max 72 bytes)")


    if not password:
        raise ValueError("Password cannot be empty")
    
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored password hash

    Returns:
        True if password matches, False otherwise
    """
    if not plain_password or not hashed_password:
        return False
    
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be no more than 128 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
        return False, "Password must contain at least one special character"
    
    return True, None


def sanitize_username(username: str) -> str:
    """
    Sanitize username input.

    Args:
        username: Raw username input

    Returns:
        Sanitized username

    Raises:
        ValueError: If username is invalid
    """
    if not username:
        raise ValueError("Username cannot be empty")
    
    # Strip whitespace
    username = username.strip()
    
    # Validate length
    if len(username) < 3:
        raise ValueError("Username must be at least 3 characters long")
    
    if len(username) > 50:
        raise ValueError("Username must be no more than 50 characters long")
    
    # Only allow alphanumeric, underscore, hyphen
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
    
    return username


def sanitize_email(email: str) -> str:
    """
    Sanitize and validate email input.

    Args:
        email: Raw email input

    Returns:
        Sanitized email (lowercase)

    Raises:
        ValueError: If email is invalid
    """
    if not email:
        raise ValueError("Email cannot be empty")
    
    # Strip and lowercase
    email = email.strip().lower()
    
    # Basic email validation
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    
    # Length check
    if len(email) > 255:
        raise ValueError("Email must be no more than 255 characters long")
    
    return email
