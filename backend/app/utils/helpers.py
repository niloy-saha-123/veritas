# Utility helpers - common functions for hashing, JSON parsing, and formatting

from typing import Any, Dict
import hashlib
import json


def generate_hash(content: str) -> str:
    """
    Generate SHA-256 hash of content.
    
    Args:
        content: String content to hash
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(content.encode()).hexdigest()


def safe_json_loads(data: str, default: Any = None) -> Any:
    """
    Safely load JSON data with fallback.
    
    Args:
        data: JSON string
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def format_location(file_path: str, line_number: int) -> str:
    """
    Format file location string.
    
    Args:
        file_path: Path to file
        line_number: Line number
        
    Returns:
        Formatted location string
    """
    return f"{file_path}:{line_number}"
