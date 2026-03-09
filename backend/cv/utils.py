"""
CV Processing Utilities
Helper functions for safe data type handling in CV/job processing.
"""
from typing import Any, Union, List


def safe_lower(value: Any) -> str:
    """
    Safely convert a value to lowercase string.
    
    Handles:
    - Lists: joins into a single string
    - None: returns empty string
    - Strings: converts to lowercase
    - Other types: converts to string first
    
    Args:
        value: Any value that might need to be lowercased
        
    Returns:
        Lowercase string representation of the value
    """
    if value is None:
        return ""
    
    if isinstance(value, list):
        # Join list items into a single string
        return " ".join(str(v) for v in value if v).lower()
    
    if isinstance(value, str):
        return value.lower()
    
    # For other types, convert to string first
    return str(value).lower() if value else ""


def safe_str(value: Any, default: str = "") -> str:
    """
    Safely convert a value to string.
    
    Args:
        value: Any value
        default: Default value if conversion fails
        
    Returns:
        String representation of the value
    """
    if value is None:
        return default
    
    if isinstance(value, list):
        return " ".join(str(v) for v in value if v)
    
    if isinstance(value, str):
        return value
    
    try:
        return str(value)
    except Exception:
        return default


def safe_list(value: Any) -> List[str]:
    """
    Safely convert a value to a list of strings.
    
    Args:
        value: Any value that might be a list, string, or other type
        
    Returns:
        List of strings
    """
    if value is None:
        return []
    
    if isinstance(value, list):
        return [str(v).strip() for v in value if v]
    
    if isinstance(value, str):
        # Split by comma or newline
        return [s.strip() for s in value.replace('\n', ',').split(',') if s.strip()]
    
    return [str(value).strip()] if value else []
