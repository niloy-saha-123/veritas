"""Module 2: User management functions."""

def get_user_info(user_id: int, include_email: bool = False) -> dict:
    """
    Get user information by ID.
    
    Args:
        user_id: Unique user identifier
        include_email: Whether to include email address
    
    Returns:
        Dictionary containing user information
    """
    return {"id": user_id, "name": "John"}

def delete_user(user_id: int, force: bool = False) -> bool:
    """
    Delete a user from the system.
    
    Args:
        user_id: User identifier
        force: Force deletion without confirmation
    
    Returns:
        True if successful
    """
    return True

def create_user(name: str, email: str) -> dict:
    """Create a new user."""
    return {"name": name, "email": email, "id": 123}
