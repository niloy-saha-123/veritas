# Markdown parser - extracts headings, code blocks, and API references

import re
from typing import List, Dict, Any
from app.models.function_signature import FunctionSignature, Parameter


def parse_markdown(code: str, filename: str = "") -> List[FunctionSignature]:
    """
    Parse Markdown and extract documented function references.
    
    Looks for:
    - Headings that look like function names (e.g., ## function_name)
    - Parameters sections with parameter lists
    - Code blocks with function signatures
    - Inline function references: `functionName(params)`
    """
    functions = []
    lines = code.split('\n')
    
    in_code_block = False
    code_block_lang = ""
    code_block_content = []
    code_block_start = 0
    
    # Track sections for function documentation
    current_heading = None
    current_heading_line = 0
    in_parameters_section = False
    in_returns_section = False
    current_section_content = []
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Track headings - check if they look like function names
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            heading_level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            
            # If this is a top-level heading (##) and looks like a function name
            # AND we have a previous function section, finalize it
            if heading_level == 2 and current_heading and _looks_like_function_name(current_heading):
                func = _parse_function_from_heading(
                    current_heading,
                    current_heading_line,
                    current_section_content,
                    filename
                )
                if func:
                    functions.append(func)
            
            # If this is a top-level heading (##), start a new section
            # Nested headings (###) are part of the current section
            if heading_level == 2:
                # Start new section
                current_heading = heading_text
                current_heading_line = line_num
                current_section_content = []
                in_parameters_section = False
                in_returns_section = False
            # For nested headings (###, ####), add them to current section content
            # They'll be used when parsing the function
            elif current_heading:
                current_section_content.append(line)
                continue
            
            # Track if this is a Parameters or Returns subsection
            if re.match(r'^#{1,6}\s+Parameters?', line, re.IGNORECASE):
                in_parameters_section = True
            elif re.match(r'^#{1,6}\s+Returns?', line, re.IGNORECASE):
                in_returns_section = True
            
            # Add the heading itself to section content for nested headings
            # Top-level headings (##) start new sections, so don't add them
            if heading_level > 2 and current_heading:
                current_section_content.append(line)
            continue
        
        # Track section content
        if current_heading:
            current_section_content.append(line)
        
        # Code block start/end
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_block_lang = line.strip()[3:].lower()
                code_block_content = []
                code_block_start = line_num
            else:
                # End of code block - parse its contents
                if code_block_content:
                    block_funcs = _parse_code_block(
                        '\n'.join(code_block_content),
                        code_block_lang,
                        code_block_start,
                        filename,
                        current_heading
                    )
                    functions.extend(block_funcs)
                in_code_block = False
            continue
        
        if in_code_block:
            code_block_content.append(line)
            continue
        
        # Look for inline function references: `functionName(params)`
        inline_funcs = _parse_inline_refs(line, line_num, filename)
        functions.extend(inline_funcs)
    
    # Finalize last heading if it looks like a function name
    if current_heading and _looks_like_function_name(current_heading):
        func = _parse_function_from_heading(
            current_heading,
            current_heading_line,
            current_section_content,
            filename
        )
        if func:
            functions.append(func)
    
    return functions


def _looks_like_function_name(text: str) -> bool:
    """Check if a heading text looks like a function name."""
    # Remove backticks if present
    text = text.strip('`')
    
    # Function names typically:
    # - Don't contain spaces (except snake_case, camelCase)
    # - Start with lowercase or underscore
    # - Contain alphanumeric, underscores, maybe camelCase
    # - Are not common section titles
    if ' ' in text and not ('_' in text or text[0].islower()):
        return False
    
    # Skip common section titles
    skip_words = ['parameters', 'parameter', 'returns', 'return', 'example', 'examples', 
                  'description', 'usage', 'notes', 'see also', 'raises', 'raises', 'warnings']
    if text.lower() in skip_words:
        return False
    
    # Check if it matches function name patterns (alphanumeric + underscore, maybe camelCase)
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$|^[a-z][a-zA-Z0-9]*$'
    return bool(re.match(pattern, text))


def _parse_function_from_heading(heading: str, heading_line: int, section_content: List[str], filename: str) -> FunctionSignature:
    """Parse a function from a heading and its section content."""
    # Extract function name (remove backticks if present)
    func_name = heading.strip('`')
    
    # Parse parameters from Parameters section
    params = []
    in_parameters_section = False
    return_type = None
    
    section_text = '\n'.join(section_content)
    
    # Extract Parameters section content
    params_match = re.search(r'(?:###\s+Parameters?|##\s+Parameters?)\s*\n(.*?)(?=\n###|\n##|\Z)', section_text, re.DOTALL | re.IGNORECASE)
    if params_match:
        params_section = params_match.group(1)
        # Pattern: - `param_name` (type): description
        # Or: - `param_name`: description (no type)
        param_patterns = [
            r'[-*]\s*`(\w+)`\s*\(([^)]+)\)',  # `name` (type): desc
            r'[-*]\s*`(\w+)`\s*:',             # `name`: desc (no type)
        ]
        
        for pattern in param_patterns:
            for match in re.finditer(pattern, params_section):
                param_name = match.group(1)
                # Extract type if pattern has second group (pattern with type)
                param_type = None
                if len(match.groups()) > 1:
                    try:
                        param_type = match.group(2).strip() if match.group(2) else None
                    except IndexError:
                        param_type = None
                # Only add if not already added
                if not any(p.name == param_name for p in params):
                    params.append(Parameter(name=param_name, type=param_type))
    
    # Find Returns section - look for pattern like "- `float`: The total price..."
    # Or "Returns: `float`" or "### Returns\n- `float`: ..."
    returns_match = re.search(r'(?:###\s+Returns?|##\s+Returns?)\s*\n.*?[-*]\s*`([^`]+)`', section_text, re.DOTALL | re.IGNORECASE)
    if returns_match:
        return_type = returns_match.group(1).strip().rstrip('.,;')
    
    return FunctionSignature(
        name=func_name,
        parameters=params,
        return_type=return_type,
        line_number=heading_line,
        file_path=filename
    )


def _parse_code_block(code: str, lang: str, start_line: int, filename: str, heading: str = None) -> List[FunctionSignature]:
    """Parse a code block for function signatures."""
    functions = []
    
    # Simple function signature patterns in documentation
    patterns = [
        # Python-style: def name(params):
        r'def\s+(\w+)\s*\(([^)]*)\)',
        # JS-style: function name(params) or name(params) =>
        r'function\s+(\w+)\s*\(([^)]*)\)',
        # Java-style: returnType name(params)
        r'(?:public|private|void|\w+)\s+(\w+)\s*\(([^)]*)\)',
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, code):
            name = match.group(1)
            params_str = match.group(2) if len(match.groups()) > 1 else ""
            
            # Skip common false positives
            if name in ('if', 'while', 'for', 'switch', 'return'):
                continue
            
            params = []
            if params_str:
                for p in params_str.split(','):
                    p = p.strip()
                    if p:
                        params.append(Parameter(name=p))
            
            functions.append(FunctionSignature(
                name=name,
                parameters=params,
                line_number=start_line,
                docstring=heading,
                file_path=filename
            ))
    
    return functions


def _parse_inline_refs(line: str, line_num: int, filename: str) -> List[FunctionSignature]:
    """Parse inline code references like `functionName(params)`."""
    functions = []
    
    # Pattern: `functionName(...)` or `moduleName.functionName(...)`
    pattern = r'`(?:[\w.]+\.)?(\w+)\(([^)]*)\)`'
    
    for match in re.finditer(pattern, line):
        name = match.group(1)
        params_str = match.group(2)
        
        # Skip common non-functions
        if name.lower() in ('print', 'log', 'console', 'example'):
            continue
        
        params = []
        if params_str:
            for p in params_str.split(','):
                p = p.strip()
                if p:
                    params.append(Parameter(name=p))
        
        functions.append(FunctionSignature(
            name=name,
            parameters=params,
            line_number=line_num,
            file_path=filename
        ))
    
    return functions


def extract_sections(code: str) -> List[Dict[str, Any]]:
    """Extract all sections from markdown (useful for doc comparison)."""
    sections = []
    lines = code.split('\n')
    
    current_section = None
    current_content = []
    
    for i, line in enumerate(lines):
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        
        if heading_match:
            if current_section:
                sections.append({
                    'level': current_section['level'],
                    'title': current_section['title'],
                    'line': current_section['line'],
                    'content': '\n'.join(current_content).strip()
                })
            
            current_section = {
                'level': len(heading_match.group(1)),
                'title': heading_match.group(2).strip(),
                'line': i + 1
            }
            current_content = []
        elif current_section:
            current_content.append(line)
    
    if current_section:
        sections.append({
            'level': current_section['level'],
            'title': current_section['title'],
            'line': current_section['line'],
            'content': '\n'.join(current_content).strip()
        })
    
    return sections
