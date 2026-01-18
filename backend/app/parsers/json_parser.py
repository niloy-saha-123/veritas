# JSON parser - extracts structure and API endpoint definitions

import json
import re
from typing import List, Dict, Any
from app.models.schemas import FunctionSignature, Parameter


def parse_json(code: str, filename: str = "") -> List[FunctionSignature]:
    """
    Parse JSON files for API definitions (OpenAPI, package.json scripts, etc).
    
    Handles: OpenAPI endpoints, package.json scripts, custom API configs
    """
    try:
        data = json.loads(code)
    except json.JSONDecodeError:
        return []
    
    functions = []
    
    # Detect JSON type and parse accordingly
    if _is_openapi(data):
        functions = _parse_openapi(data, filename)
    elif _is_package_json(data):
        functions = _parse_package_json(data, filename)
    else:
        # Generic API config parser
        functions = _parse_generic_api(data, filename)
    
    return functions


def _is_openapi(data: dict) -> bool:
    """Check if JSON is OpenAPI/Swagger spec."""
    return 'openapi' in data or 'swagger' in data or 'paths' in data


def _is_package_json(data: dict) -> bool:
    """Check if JSON is package.json."""
    return 'name' in data and ('scripts' in data or 'dependencies' in data)


def _parse_openapi(data: dict, filename: str) -> List[FunctionSignature]:
    """Parse OpenAPI spec for endpoint definitions."""
    functions = []
    
    paths = data.get('paths', {})
    
    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        
        for method, details in methods.items():
            if method.startswith('x-') or not isinstance(details, dict):
                continue
            
            name = details.get('operationId', f"{method.upper()} {path}")
            summary = details.get('summary', details.get('description', ''))
            
            # Extract parameters
            params = []
            for param in details.get('parameters', []):
                if isinstance(param, dict):
                    params.append(Parameter(
                        name=param.get('name', 'param'),
                        type=param.get('schema', {}).get('type', param.get('in'))
                    ))
            
            # Extract response type
            responses = details.get('responses', {})
            return_type = None
            if '200' in responses:
                resp = responses['200']
                if isinstance(resp, dict):
                    return_type = resp.get('description', 'Success')
            
            functions.append(FunctionSignature(
                name=name,
                params=params,
                return_type=return_type,
                docstring=summary,
                filename=filename
            ))
    
    return functions


def _parse_package_json(data: dict, filename: str) -> List[FunctionSignature]:
    """Parse package.json for npm scripts."""
    functions = []
    
    scripts = data.get('scripts', {})
    for name, command in scripts.items():
        functions.append(FunctionSignature(
            name=f"npm run {name}",
            params=[],
            docstring=command,
            filename=filename
        ))
    
    return functions


def _parse_generic_api(data: dict, filename: str, prefix: str = "") -> List[FunctionSignature]:
    """Parse generic JSON for function-like patterns."""
    functions = []
    
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            # Check if it looks like an endpoint/function definition
            if 'url' in value or 'endpoint' in value or 'method' in value:
                functions.append(FunctionSignature(
                    name=key,
                    params=[],
                    docstring=str(value.get('description', '')),
                    filename=filename
                ))
            else:
                # Recurse into nested objects
                functions.extend(_parse_generic_api(value, filename, full_key))
    
    return functions


def extract_structure(code: str) -> Dict[str, Any]:
    """Extract full JSON structure for comparison."""
    try:
        return json.loads(code)
    except json.JSONDecodeError:
        return {}
