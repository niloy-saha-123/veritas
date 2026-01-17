# Test suite for code and documentation parsers

"""Tests for code and documentation parsers."""

import pytest
from app.services.code_parser import CodeParser
from app.services.doc_parser import DocParser


class TestCodeParser:
    """Test cases for CodeParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CodeParser()
    
    def test_parse_python_function(self):
        """Test parsing a simple Python function."""
        code = '''
def hello_world(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"
'''
        result = self.parser.parse(code, "python")
        
        assert "functions" in result
        assert len(result["functions"]) == 1
        assert result["functions"][0]["name"] == "hello_world"
        assert "name" in result["functions"][0]["parameters"]
    
    def test_parse_python_class(self):
        """Test parsing a Python class."""
        code = '''
class Calculator:
    """A simple calculator class."""
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
'''
        result = self.parser.parse(code, "python")
        
        assert "classes" in result
        assert len(result["classes"]) == 1
        assert result["classes"][0]["name"] == "Calculator"
        assert len(result["classes"][0]["methods"]) == 1


class TestDocParser:
    """Test cases for DocParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = DocParser()
    
    def test_parse_markdown_sections(self):
        """Test extracting sections from markdown."""
        content = '''
# Main Title
## Subsection
### API Reference
'''
        result = self.parser.parse(content, "markdown")
        
        assert "sections" in result
        assert len(result["sections"]) == 3
        assert result["sections"][0]["title"] == "Main Title"
    
    def test_parse_code_blocks(self):
        """Test extracting code blocks from markdown."""
        content = '''
Example usage:

```python
def example():
    pass
```
'''
        result = self.parser.parse(content, "markdown")
        
        assert "code_blocks" in result
        assert len(result["code_blocks"]) == 1
        assert result["code_blocks"][0]["language"] == "python"
