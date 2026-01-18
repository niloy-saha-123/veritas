# Parser Factory - auto-detects language from filename and routes to correct parser

from typing import List
from app.models.function_signature import FunctionSignature


def parse_code(filename: str, code: str) -> List[FunctionSignature]:
    """
    Parse code and extract function signatures - auto-detects language from filename.
    
    Supported: .java, .md, .markdown, .json, .py, .js, .jsx, .ts, .tsx
    """
    if not code or not code.strip():
        return []
    
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.java'):
        return _parse_java(code, filename)
    elif filename_lower.endswith(('.md', '.markdown')):
        return _parse_markdown(code, filename)
    elif filename_lower.endswith('.json'):
        return _parse_json(code, filename)
    elif filename_lower.endswith('.py'):
        return _parse_python(code, filename)
    elif filename_lower.endswith(('.js', '.jsx')):
        return _parse_javascript(code, filename)
    elif filename_lower.endswith(('.ts', '.tsx')):
        return _parse_typescript(code, filename)
    else:
        # Not an error - just unsupported file type
        return []


def get_supported_extensions() -> List[str]:
    """Get list of supported file extensions."""
    return ['.java', '.md', '.markdown', '.json', '.py', '.js', '.jsx', '.ts', '.tsx']


def is_supported(filename: str) -> bool:
    """Check if a file type is supported."""
    return any(filename.lower().endswith(ext) for ext in get_supported_extensions())


# ============================================================================
# INTERNAL - Route to actual parsers
# ============================================================================

def _parse_java(code: str, filename: str) -> List[FunctionSignature]:
    try:
        from .java_parser import parse_java
        return parse_java(code, filename)
    except Exception as e:
        print(f"Error parsing Java file {filename}: {e}")
        return []


def _parse_markdown(code: str, filename: str) -> List[FunctionSignature]:
    try:
        from .markdown_parser import parse_markdown
        return parse_markdown(code, filename)
    except Exception as e:
        print(f"Error parsing Markdown file {filename}: {e}")
        return []


def _parse_json(code: str, filename: str) -> List[FunctionSignature]:
    try:
        from .json_parser import parse_json
        return parse_json(code, filename)
    except Exception as e:
        print(f"Error parsing JSON file {filename}: {e}")
        return []


def _parse_python(code: str, filename: str) -> List[FunctionSignature]:
    try:
        from .python_parser import parse_python
        return parse_python(code, filename)
    except Exception as e:
        print(f"Error parsing Python file {filename}: {e}")
        return []


def _parse_javascript(code: str, filename: str) -> List[FunctionSignature]:
    try:
        from .javascript_parser import parse_javascript
        return parse_javascript(code, filename)
    except Exception as e:
        print(f"Error parsing JavaScript file {filename}: {e}")
        return []


def _parse_typescript(code: str, filename: str) -> List[FunctionSignature]:
    try:
        from .javascript_parser import parse_typescript
        return parse_typescript(code, filename)
    except Exception as e:
        print(f"Error parsing TypeScript file {filename}: {e}")
        return []


# ============================================================================
# BATCH UTILITIES
# ============================================================================

def parse_multiple_files(files: dict) -> dict:
    """Parse multiple files at once."""
    results = {}
    for filename, code in files.items():
        functions = parse_code(filename, code)
        results[filename] = functions
    return results


def get_all_functions(files: dict) -> List[FunctionSignature]:
    """Parse multiple files and return all functions as a flat list."""
    all_functions = []
    for functions in parse_multiple_files(files).values():
        all_functions.extend(functions)
    return all_functions
