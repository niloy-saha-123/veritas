# Code parser - extracts functions, classes, and metadata from source code using Python AST

import ast
from typing import Dict, List, Any, Optional


class CodeParser:
    """
    Service for parsing source code and extracting relevant information.
    Supports multiple programming languages with extensible architecture.
    """
    
    def __init__(self):
        """Initialize the code parser."""
        self.supported_languages = ["python", "javascript", "typescript"]
    
    def parse(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Parse source code and extract structure.
        
        Args:
            code: Source code string
            language: Programming language
            
        Returns:
            Parsed code structure with functions, classes, and metadata
        """
        if language.lower() == "python":
            return self._parse_python(code)
        else:
            # TODO: Implement parsers for other languages
            return {"error": f"Parser for {language} not yet implemented"}
    
    def _parse_python(self, code: str) -> Dict[str, Any]:
        """
        Parse Python code using AST.
        
        Args:
            code: Python source code
            
        Returns:
            Structured representation of the code
        """
        try:
            tree = ast.parse(code)
            
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(self._extract_function_info(node))
                elif isinstance(node, ast.ClassDef):
                    classes.append(self._extract_class_info(node))
            
            return {
                "language": "python",
                "functions": functions,
                "classes": classes,
                "imports": self._extract_imports(tree)
            }
        except SyntaxError as e:
            return {"error": f"Syntax error in Python code: {str(e)}"}
    
    def _extract_function_info(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract information from a function definition."""
        return {
            "name": node.name,
            "line_number": node.lineno,
            "parameters": [arg.arg for arg in node.args.args],
            "docstring": ast.get_docstring(node),
            "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list]
        }
    
    def _extract_class_info(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract information from a class definition."""
        methods = [
            self._extract_function_info(n) 
            for n in node.body 
            if isinstance(n, ast.FunctionDef)
        ]
        
        return {
            "name": node.name,
            "line_number": node.lineno,
            "methods": methods,
            "docstring": ast.get_docstring(node),
            "bases": [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
        }
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.extend([f"{module}.{alias.name}" for alias in node.names])
        return imports
