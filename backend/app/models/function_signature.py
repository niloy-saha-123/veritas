from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Parameter:
    """Represents a function parameter"""
    name: str
    type: Optional[str] = None
    default: Optional[str] = None

@dataclass
class FunctionSignature:
    """Represents a parsed function from code"""
    name: str
    parameters: List[Parameter]
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    line_number: int
    file_path: str
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "default": p.default
                } for p in self.parameters
            ],
            "return_type": self.return_type,
            "docstring": self.docstring,
            "line_number": self.line_number,
            "file_path": self.file_path
        }