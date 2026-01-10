"""
Input Sanitization Utilities
Production-grade input sanitization to prevent XSS and injection attacks.
"""

import html
import json
import re
from typing import Any


def sanitize_string(value: str, max_length: int = 10000, allow_html: bool = False) -> str:
    """
    Sanitize string input to prevent XSS.
    
    Args:
        value: Input string
        max_length: Maximum allowed length
        allow_html: If True, allows safe HTML (not recommended for user input)
    
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Truncate if too long
    if len(value) > max_length:
        value = value[:max_length]
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Remove control characters (except newline, tab, carriage return)
    value = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', value)
    
    if not allow_html:
        # Escape HTML entities
        value = html.escape(value, quote=True)
    
    return value.strip()


def sanitize_html(value: str, max_length: int = 50000) -> str:
    """
    Sanitize HTML content (more permissive than sanitize_string).
    
    WARNING: This is a basic sanitizer. For production, consider using
    a library like bleach for more comprehensive HTML sanitization.
    
    Args:
        value: HTML string
        max_length: Maximum allowed length
    
    Returns:
        Sanitized HTML string
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Truncate if too long
    if len(value) > max_length:
        value = value[:max_length]
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Remove script tags and event handlers (basic protection)
    value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r'on\w+\s*=', '', value, flags=re.IGNORECASE)
    
    return value.strip()


def sanitize_dict(data: dict[str, Any], max_depth: int = 10, current_depth: int = 0) -> dict[str, Any]:
    """
    Recursively sanitize dictionary values.
    
    Args:
        data: Dictionary to sanitize
        max_depth: Maximum nesting depth
        current_depth: Current recursion depth
    
    Returns:
        Sanitized dictionary
    """
    if current_depth >= max_depth:
        return {}
    
    sanitized = {}
    for key, value in data.items():
        # Sanitize key
        safe_key = sanitize_string(str(key), max_length=100)
        
        if isinstance(value, str):
            sanitized[safe_key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[safe_key] = sanitize_dict(value, max_depth, current_depth + 1)
        elif isinstance(value, list):
            sanitized[safe_key] = [
                sanitize_dict(item, max_depth, current_depth + 1) if isinstance(item, dict)
                else sanitize_string(str(item)) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            # For other types, convert to string and sanitize
            sanitized[safe_key] = sanitize_string(str(value), max_length=1000)
    
    return sanitized


def sanitize_json(value: str, max_size: int = 1048576) -> dict[str, Any]:
    """
    Parse and sanitize JSON string.
    
    Args:
        value: JSON string
        max_size: Maximum JSON size in bytes
    
    Returns:
        Sanitized dictionary
    
    Raises:
        ValueError: If JSON is invalid or too large
    """
    if len(value) > max_size:
        raise ValueError(f"JSON payload exceeds maximum size of {max_size} bytes")
    
    try:
        data = json.loads(value)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {str(e)}")
    
    if isinstance(data, dict):
        return sanitize_dict(data)
    elif isinstance(data, list):
        return [
            sanitize_dict(item, max_depth=10) if isinstance(item, dict)
            else sanitize_string(str(item)) if isinstance(item, str)
            else item
            for item in data
        ]
    else:
        return sanitize_string(str(data))


def validate_uuid(value: str) -> str:
    """
    Validate and sanitize UUID string.
    
    Args:
        value: UUID string
    
    Returns:
        Sanitized UUID string
    
    Raises:
        ValueError: If UUID format is invalid
    """
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    value = value.strip().lower()
    
    if not re.match(uuid_pattern, value):
        raise ValueError("Invalid UUID format")
    
    return value


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other attacks.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    
    # Remove null bytes
    filename = filename.replace('\x00', '')
    
    # Remove control characters
    filename = re.sub(r'[\x00-\x1F\x7F]', '', filename)
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename.strip()
