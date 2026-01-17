from typing import List
from ..models.function_signature import FunctionSignature
from .python_parser import parse_python
from .javascript_parser import parse_javascript


def parse_code(code: str, file_path: str) -> List[FunctionSignature]:
    """
    Auto-detect language from file extension and parse code
    
    Supported languages:
    - Python (.py)
    - JavaScript (.js, .jsx)
    - TypeScript (.ts, .tsx)
    
    Args:
        code: Source code as string
        file_path: Filename with extension
    
    Returns:
        List of FunctionSignature objects
    """
    
    if file_path.endswith('.py'):
        return parse_python(code, file_path)
    
    elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
        return parse_javascript(code, file_path)
    
    else:
        print(f"⚠️ Unsupported file type: {file_path}")
        return []


# Convenience function to check if file is supported
def is_supported_language(file_path: str) -> bool:
    """Check if file extension is supported"""
    return file_path.endswith(('.py', '.js', '.jsx', '.ts', '.tsx')) 