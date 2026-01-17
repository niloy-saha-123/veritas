# Documentation parser - extracts API references and code examples from Markdown docs

import re
from typing import Dict, List, Any, Optional


class DocParser:
    """
    Service for parsing documentation and extracting API references,
    function signatures, and code examples.
    """
    
    def __init__(self):
        """Initialize the documentation parser."""
        self.supported_formats = ["markdown", "rst", "html"]
    
    def parse(self, content: str, format: str = "markdown") -> Dict[str, Any]:
        """
        Parse documentation content.
        
        Args:
            content: Documentation content
            format: Documentation format (markdown, rst, html)
            
        Returns:
            Parsed documentation structure
        """
        if format.lower() == "markdown":
            return self._parse_markdown(content)
        else:
            # TODO: Implement parsers for other formats
            return {"error": f"Parser for {format} not yet implemented"}
    
    def _parse_markdown(self, content: str) -> Dict[str, Any]:
        """
        Parse Markdown documentation.
        
        Args:
            content: Markdown content
            
        Returns:
            Structured documentation data
        """
        return {
            "format": "markdown",
            "sections": self._extract_sections(content),
            "code_blocks": self._extract_code_blocks(content),
            "api_references": self._extract_api_references(content)
        }
    
    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """Extract sections from markdown content."""
        sections = []
        pattern = r'^(#{1,6})\s+(.+)$'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            level = len(match.group(1))
            title = match.group(2).strip()
            sections.append({
                "level": level,
                "title": title,
                "line": content[:match.start()].count('\n') + 1
            })
        
        return sections
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Extract code blocks from markdown."""
        code_blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1) or "unknown"
            code = match.group(2).strip()
            code_blocks.append({
                "language": language,
                "code": code,
                "line": content[:match.start()].count('\n') + 1
            })
        
        return code_blocks
    
    def _extract_api_references(self, content: str) -> List[Dict[str, str]]:
        """Extract API function/method references from documentation."""
        # TODO: Implement more sophisticated API reference extraction
        # Look for patterns like:
        # - `function_name(params)`
        # - **function_name** - description
        # - ### function_name
        
        api_refs = []
        
        # Simple pattern for inline code references
        pattern = r'`([a-zA-Z_][a-zA-Z0-9_]*)\((.*?)\)`'
        
        for match in re.finditer(pattern, content):
            function_name = match.group(1)
            parameters = match.group(2)
            api_refs.append({
                "name": function_name,
                "parameters": parameters,
                "line": content[:match.start()].count('\n') + 1
            })
        
        return api_refs
