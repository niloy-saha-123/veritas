import re
from typing import List
from ..models.function_signature import FunctionSignature, Parameter


def parse_javascript(code: str, file_path: str) -> List[FunctionSignature]:
    """
    Parse JavaScript or TypeScript code using regex
    Simple but effective for hackathon MVP
    
    Args:
        code: JS/TS source code as string
        file_path: Path to the file
    
    Returns:
        List of FunctionSignature objects
    """
    functions = []
    
    # Pattern 1: function declarations
    # Matches: function name(param1: type, param2: type): returnType { ... }
    func_pattern = r'function\s+(\w+)\s*\((.*?)\)(?:\s*:\s*([\w<>\[\]]+))?\s*\{'
    
    for match in re.finditer(func_pattern, code):
        name = match.group(1)
        params_str = match.group(2)
        return_type = match.group(3)
        
        parameters = _parse_params_string(params_str)
        line_number = code[:match.start()].count('\n') + 1
        
        functions.append(FunctionSignature(
            name=name,
            parameters=parameters,
            return_type=return_type,
            docstring=None,
            line_number=line_number,
            file_path=file_path
        ))
    
    # Pattern 2: arrow functions
    # Matches: const func = (params) => { ... } or const func = (params): type => { ... }
    arrow_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*\((.*?)\)(?:\s*:\s*([\w<>\[\]]+))?\s*=>'
    
    for match in re.finditer(arrow_pattern, code):
        name = match.group(1)
        params_str = match.group(2)
        return_type = match.group(3)
        
        parameters = _parse_params_string(params_str)
        line_number = code[:match.start()].count('\n') + 1
        
        functions.append(FunctionSignature(
            name=name,
            parameters=parameters,
            return_type=return_type,
            docstring=None,
            line_number=line_number,
            file_path=file_path
        ))
    
    # Pattern 3: class methods (TypeScript/ES6)
    # Matches: methodName(params): returnType { ... }
    method_pattern = r'(?:public|private|protected)?\s*(?:async)?\s*(\w+)\s*\((.*?)\)(?:\s*:\s*([\w<>\[\]]+))?\s*\{'
    
    for match in re.finditer(method_pattern, code):
        name = match.group(1)
        # Skip constructors and common non-method words
        if name in ['if', 'while', 'for', 'switch', 'catch', 'constructor']:
            continue
            
        params_str = match.group(2)
        return_type = match.group(3)
        
        parameters = _parse_params_string(params_str)
        line_number = code[:match.start()].count('\n') + 1
        
        functions.append(FunctionSignature(
            name=name,
            parameters=parameters,
            return_type=return_type,
            docstring=None,
            line_number=line_number,
            file_path=file_path
        ))
    
    return functions


def _parse_params_string(params_str: str) -> List[Parameter]:
    """
    Parse parameter string into Parameter objects
    Handles: 'email: string, password: string, token?: string = null'
    """
    if not params_str.strip():
        return []
    
    parameters = []
    
    for param in params_str.split(','):
        param = param.strip()
        if not param:
            continue
        
        # Remove optional marker (?)
        is_optional = '?' in param
        param = param.replace('?', '')
        
        # Handle TypeScript: 'email: string = "default"'
        if ':' in param:
            name_part, type_part = param.split(':', 1)
            name = name_part.strip()
            
            # Check for default value
            if '=' in type_part:
                type_str, default = type_part.split('=', 1)
                param_type = type_str.strip()
                param_default = default.strip()
            else:
                param_type = type_part.strip()
                param_default = None
                
        else:
            # Plain JavaScript: just 'email'
            if '=' in param:
                name, default = param.split('=', 1)
                name = name.strip()
                param_type = None
                param_default = default.strip()
            else:
                name = param.strip()
                param_type = None
                param_default = None
        
        parameters.append(Parameter(
            name=name,
            type=param_type,
            default=param_default
        ))
    
    return parameters


def parse_typescript(code: str, file_path: str) -> List[FunctionSignature]:
    """
    Parse TypeScript code using the same parser as JavaScript.
    
    Args:
        code: TypeScript source code as string
        file_path: Path to the file
    
    Returns:
        List of FunctionSignature objects
    """
    # TypeScript syntax is similar to JavaScript, so we can reuse the JavaScript parser
    return parse_javascript(code, file_path)