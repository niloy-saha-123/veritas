import ast
from typing import List, Optional
from ..models.function_signature import FunctionSignature, Parameter


def parse_python(code: str, file_path: str) -> List[FunctionSignature]:
    """
    Extract function signatures from Python code.
    
    Only extracts top-level functions (not nested functions or methods inside classes).
    Skips private functions starting with '_' unless they're special methods (__init__, etc.).
    
    Args:
        code: Python source code as string
        file_path: Path to the file (for tracking)
    
    Returns:
        List of FunctionSignature objects
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        print(f"⚠️ Syntax error in {file_path}: {e}")
        return []
    
    functions = []
    
    # Only extract top-level functions (not nested inside classes/functions)
    # Use iter_child_nodes instead of walk to avoid getting nested functions
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            # Only skip if it's clearly a test file AND a test function
            # Don't skip private functions - they're still valid functions
            is_test_file = 'test' in file_path.lower() and ('test' in file_path or 'spec' in file_path)
            is_test_func = node.name.startswith('test_') or 'test' in node.name.lower()
            
            if is_test_file and is_test_func:
                continue
            
            func = _extract_function(node, file_path)
            functions.append(func)
        elif isinstance(node, ast.ClassDef):
            # Extract methods from classes
            # Only skip test methods in actual test files
            is_test_file = 'test' in file_path.lower() and ('test' in file_path or 'spec' in file_path)
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.FunctionDef):
                    is_test_method = child.name.startswith('test_') or 'test' in child.name.lower()
                    
                    # Only skip test methods in test files
                    if is_test_file and is_test_method:
                        continue
                    
                    # Extract all other methods (including private ones - they're still methods)
                    func = _extract_function(child, file_path)
                    functions.append(func)
    
    return functions


def _extract_function(node: ast.FunctionDef, file_path: str) -> FunctionSignature:
    """Extract details from a single function node"""
    
    # Get function name
    name = node.name
    
    # Get parameters
    parameters = []
    for arg in node.args.args:
        param = Parameter(
            name=arg.arg,
            type=_get_annotation(arg.annotation),
            default=None
        )
        parameters.append(param)
    
    # Handle default values (aligned from right)
    defaults = node.args.defaults
    if defaults:
        for i, default in enumerate(defaults):
            param_index = len(parameters) - len(defaults) + i
            parameters[param_index].default = ast.unparse(default)
    
    # Get return type
    return_type = _get_annotation(node.returns)
    
    # Get docstring
    docstring = ast.get_docstring(node)
    
    # Get line number
    line_number = node.lineno
    
    return FunctionSignature(
        name=name,
        parameters=parameters,
        return_type=return_type,
        docstring=docstring,
        line_number=line_number,
        file_path=file_path
    )


def _get_annotation(annotation) -> Optional[str]:
    """Convert type annotation to string"""
    if annotation is None:
        return None
    try:
        return ast.unparse(annotation)
    except:
        return None