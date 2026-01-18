# Java parser - extracts class/method signatures using regex patterns

import re
from typing import List, Optional
from app.models.function_signature import FunctionSignature, Parameter


def parse_java(code: str, filename: str = "") -> List[FunctionSignature]:
    """
    Parse Java code and extract method signatures.
    
    Handles: class methods, constructors, static methods, interfaces
    """
    functions = []
    lines = code.split('\n')
    
    current_class = None
    
    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()
        
        # Track class context
        class_match = re.match(r'^(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)', stripped)
        if class_match:
            current_class = class_match.group(1)
            continue
        
        # Interface
        interface_match = re.match(r'^(?:public\s+)?interface\s+(\w+)', stripped)
        if interface_match:
            current_class = interface_match.group(1)
            continue
        
        # Parse method signature
        # Pattern: (modifiers) returnType methodName(params) (throws...)? {
        method_pattern = r'^(public\s+|private\s+|protected\s+)?(static\s+)?(final\s+)?(synchronized\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)'
        match = re.match(method_pattern, stripped)
        
        if match:
            return_type = match.group(5)
            name = match.group(6)
            params_str = match.group(7)
            
            # Skip if it's a control statement
            if name in ('if', 'while', 'for', 'switch', 'catch'):
                continue
            
            params = _parse_java_params(params_str)
            
            functions.append(FunctionSignature(
                name=name,
                parameters=params,
                return_type=return_type,
                line_number=line_num,
                file_path=filename
            ))
            continue
        
        # Constructor pattern: ClassName(params) {
        if current_class:
            constructor_pattern = rf'^(public\s+|private\s+|protected\s+)?{current_class}\s*\(([^)]*)\)'
            match = re.match(constructor_pattern, stripped)
            if match:
                params = _parse_java_params(match.group(2))
                functions.append(FunctionSignature(
                    name=current_class,
                    parameters=params,
                    return_type=None,
                    line_number=line_num,
                    file_path=filename
                ))
    
    # Attach Javadoc comments
    _attach_javadoc(code, functions)
    
    return functions


def _parse_java_params(params_str: str) -> List[Parameter]:
    """Parse Java parameter string: Type name, Type2 name2"""
    params = []
    if not params_str.strip():
        return params
    
    # Split by comma
    parts = params_str.split(',')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Pattern: (final )? Type name or Type... name (varargs)
        match = re.match(r'(final\s+)?(\w+(?:<[^>]+>)?(?:\[\])?(?:\.\.\.)?)\s+(\w+)', part)
        if match:
            param_type = match.group(2)
            name = match.group(3)
            params.append(Parameter(name=name, type=param_type))
        else:
            params.append(Parameter(name=part))
    
    return params


def _attach_javadoc(code: str, functions: List[FunctionSignature]) -> None:
    """Extract Javadoc comments and attach to methods."""
    lines = code.split('\n')
    
    for func in functions:
        start = func.line_number - 2
        javadoc_lines = []
        in_javadoc = False
        
        for i in range(start, max(-1, start - 30), -1):
            if i < 0:
                break
            line = lines[i].strip()
            
            if line.endswith('*/'):
                in_javadoc = True
                javadoc_lines.insert(0, line)
            elif in_javadoc:
                javadoc_lines.insert(0, line)
                if line.startswith('/**'):
                    break
            elif line and not line.startswith('//') and not line.startswith('@'):
                break
        
        if javadoc_lines:
            javadoc = '\n'.join(javadoc_lines)
            javadoc = re.sub(r'/\*\*|\*/', '', javadoc)
            javadoc = re.sub(r'^\s*\*\s?', '', javadoc, flags=re.MULTILINE)
            func.docstring = javadoc.strip()
