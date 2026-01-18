import ast
from typing import List, Optional
from ..models.function_signature import FunctionSignature, Parameter


def parse_python(code: str, file_path: str) -> List[FunctionSignature]:
    """
    Extract all function signatures from Python code
    
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
    
    # Walk through all nodes in the AST
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func = _extract_function(node, file_path)
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