# Markdown parser - extracts headings, code blocks, and API references

import re
from typing import List, Dict, Any
from app.models.schemas import FunctionSignature, Parameter


def parse_markdown(code: str, filename: str = "") -> List[FunctionSignature]:
    """
    Parse Markdown and extract documented function references.
    
    Looks for: code blocks with function signatures, API documentation patterns
    """
    functions = []
    lines = code.split('\n')
    
    in_code_block = False
    code_block_lang = ""
    code_block_content = []
    code_block_start = 0
    
    current_heading = None
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Track headings for context
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            current_heading = heading_match.group(2).strip()
            continue
        
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
    
    return functions


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
                params=params,
                line_number=start_line,
                docstring=heading,
                filename=filename
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
            params=params,
            line_number=line_num,
            filename=filename
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
