# backend/app/github/doc_generator.py
"""
AI-powered documentation generator using Gemini.

Generates professional documentation for functions that are missing docs.
Uses the actual code to understand what the function does and creates
accurate, helpful documentation.
"""

import json
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass

from app.core.config import settings
from app.models.function_signature import FunctionSignature


@dataclass
class GeneratedDoc:
    """Generated documentation for a function."""
    function_name: str
    markdown: str
    summary: str


class DocGenerator:
    """
    AI-powered documentation generator.

    Uses Gemini to analyze function signatures and code to generate
    professional-quality documentation.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = "gemini-2.5-flash"

    def generate_docs_for_functions(
        self,
        functions: List[FunctionSignature],
        code_context: Optional[str] = None
    ) -> str:
        """
        Generate documentation for multiple functions.

        Args:
            functions: List of function signatures to document
            code_context: Optional surrounding code for better context

        Returns:
            Markdown documentation string
        """
        if not functions:
            return ""

        # Generate docs for each function
        all_docs = []
        for func in functions:
            doc = self._generate_single_doc(func, code_context)
            if doc:
                all_docs.append(doc)

        # Combine into markdown
        return self._format_markdown(all_docs)

    def _generate_single_doc(
        self,
        func: FunctionSignature,
        code_context: Optional[str] = None
    ) -> Optional[GeneratedDoc]:
        """Generate documentation for a single function."""

        prompt = self._build_prompt(func, code_context)

        try:
            response = self._call_gemini(prompt)
            return self._parse_response(response, func.name)
        except Exception as e:
            print(f"Error generating docs for {func.name}: {e}")
            # Fallback to basic docs
            return self._generate_basic_doc(func)

    def _build_prompt(
        self,
        func: FunctionSignature,
        code_context: Optional[str] = None
    ) -> str:
        """Build the prompt for Gemini."""

        # Format parameters
        params_info = []
        for p in func.parameters:
            param_str = f"- {p.name}"
            if p.type:
                param_str += f" (type: {p.type})"
            if p.default:
                param_str += f" (default: {p.default})"
            params_info.append(param_str)

        params_section = "\n".join(params_info) if params_info else "No parameters"

        context_section = ""
        if code_context:
            context_section = f"""
SURROUNDING CODE CONTEXT:
```
{code_context[:2000]}
```
"""

        return f"""You are a technical documentation writer. Generate clear, professional documentation for this function.

FUNCTION TO DOCUMENT:
- Name: {func.name}
- File: {func.file_path}
- Line: {func.line_number}
- Parameters:
{params_section}
- Return Type: {func.return_type or 'Not specified'}
- Existing Docstring: {func.docstring or 'None'}
{context_section}

INSTRUCTIONS:
1. Analyze the function name, parameters, and any context to understand its purpose
2. Write a clear, concise summary (1-2 sentences)
3. Document each parameter with its purpose and expected values
4. Document the return value
5. Include a simple usage example if helpful

Respond with JSON only:
{{
  "summary": "Brief description of what the function does",
  "parameters": [
    {{
      "name": "param_name",
      "type": "param_type",
      "description": "What this parameter is for"
    }}
  ],
  "returns": {{
    "type": "return_type",
    "description": "What the function returns"
  }},
  "example": "Optional usage example"
}}
"""

    def _call_gemini(self, prompt: str) -> str:
        """Call the Gemini API."""

        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=60
        )

        response.raise_for_status()
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]

    def _parse_response(self, response: str, func_name: str) -> GeneratedDoc:
        """Parse the Gemini response into a GeneratedDoc."""

        # Extract JSON from response
        start = response.find("{")
        end = response.rfind("}") + 1
        json_str = response[start:end] if start != -1 and end > start else "{}"

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return self._generate_basic_doc_from_name(func_name)

        # Build markdown
        markdown = f"## `{func_name}`\n\n"
        markdown += f"{data.get('summary', 'No description available.')}\n\n"

        # Parameters
        params = data.get("parameters", [])
        if params:
            markdown += "### Parameters\n\n"
            for p in params:
                ptype = f" (`{p.get('type', 'any')}`)" if p.get("type") else ""
                markdown += f"- **{p.get('name', 'unknown')}**{ptype}: {p.get('description', '')}\n"
            markdown += "\n"

        # Returns
        returns = data.get("returns", {})
        if returns:
            rtype = f"`{returns.get('type', 'any')}`" if returns.get("type") else ""
            markdown += "### Returns\n\n"
            markdown += f"- {rtype}: {returns.get('description', 'Return value')}\n\n"

        # Example
        example = data.get("example")
        if example:
            markdown += "### Example\n\n"
            markdown += f"```python\n{example}\n```\n\n"

        markdown += "---\n\n"

        return GeneratedDoc(
            function_name=func_name,
            markdown=markdown,
            summary=data.get("summary", "")
        )

    def _generate_basic_doc(self, func: FunctionSignature) -> GeneratedDoc:
        """Generate basic documentation without AI (fallback)."""

        markdown = f"## `{func.name}`\n\n"

        # Try to generate a summary from the function name
        readable_name = func.name.replace("_", " ").title()
        markdown += f"{readable_name}.\n\n"

        # Parameters
        if func.parameters:
            markdown += "### Parameters\n\n"
            for p in func.parameters:
                ptype = f" (`{p.type}`)" if p.type else ""
                default = f" (default: `{p.default}`)" if p.default else ""
                markdown += f"- **{p.name}**{ptype}{default}\n"
            markdown += "\n"

        # Return type
        if func.return_type:
            markdown += "### Returns\n\n"
            markdown += f"- `{func.return_type}`\n\n"

        markdown += "---\n\n"

        return GeneratedDoc(
            function_name=func.name,
            markdown=markdown,
            summary=readable_name
        )

    def _generate_basic_doc_from_name(self, func_name: str) -> GeneratedDoc:
        """Generate minimal documentation from just the function name."""
        readable_name = func_name.replace("_", " ").title()
        markdown = f"## `{func_name}`\n\n{readable_name}.\n\n---\n\n"
        return GeneratedDoc(
            function_name=func_name,
            markdown=markdown,
            summary=readable_name
        )

    def _format_markdown(self, docs: List[GeneratedDoc]) -> str:
        """Format multiple docs into a single markdown document."""

        if not docs:
            return ""

        # Header
        content = "# API Documentation\n\n"
        content += "> Auto-generated by Veritas\n\n"

        # Table of contents
        content += "## Table of Contents\n\n"
        for doc in docs:
            anchor = doc.function_name.lower().replace("_", "-")
            content += f"- [{doc.function_name}](#{anchor})\n"
        content += "\n---\n\n"

        # All docs
        for doc in docs:
            content += doc.markdown

        return content


def generate_docs_for_pr(
    undocumented_functions: List[FunctionSignature],
    code_snippets: Optional[Dict[str, str]] = None
) -> str:
    """
    Generate documentation for functions missing from a PR.

    Args:
        undocumented_functions: List of functions without documentation
        code_snippets: Optional dict of {func_name: code_context}

    Returns:
        Markdown documentation string
    """
    generator = DocGenerator()
    return generator.generate_docs_for_functions(
        undocumented_functions,
        code_context=None  # Could pass combined snippets here
    )


def generate_pr_body(
    functions: List[FunctionSignature],
    related_pr: int
) -> str:
    """Generate PR description for documentation PR."""

    func_list = "\n".join(f"- `{f.name}()`" for f in functions[:20])
    if len(functions) > 20:
        func_list += f"\n- ...and {len(functions) - 20} more"

    return f"""## Documentation Update

This PR adds documentation for **{len(functions)} new function(s)** introduced in #{related_pr}.

### Functions Documented

{func_list}

### Why This PR?

The Veritas documentation agent detected new functions without corresponding documentation.
This auto-generated documentation helps maintain code-documentation consistency.

### Review Notes

- Please review the generated documentation for accuracy
- Feel free to edit and improve the descriptions
- Merge when the documentation meets your standards

---
*Auto-generated by [Veritas](https://veritas.dev) - Documentation Verification Agent*
"""


def generate_issue_body(
    issues: List[Dict],
    related_pr: int
) -> str:
    """Generate issue description for documentation mismatch."""

    body = f"""## Documentation Mismatch Detected

Veritas found **{len(issues)} documentation issue(s)** in PR #{related_pr} that need attention.

### Issues Found

"""

    for i, issue in enumerate(issues[:10], 1):
        severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
            issue.get("severity", "medium"), "🟡"
        )

        body += f"""#### {i}. {severity_emoji} `{issue.get('function', 'Unknown')}`

**Problem:** {issue.get('issue', 'Unknown issue')}

| Code Says | Docs Say |
|-----------|----------|
| `{issue.get('code_has', 'N/A')}` | `{issue.get('docs_say', 'N/A')}` |

**Suggested Fix:** {issue.get('suggested_fix', 'Update documentation to match code')}

---

"""

    if len(issues) > 10:
        body += f"\n*...and {len(issues) - 10} more issues*\n\n"

    body += """### How to Fix

1. Review each issue above
2. Update either the code or documentation to match
3. Close this issue when resolved

---
*Generated by [Veritas](https://veritas.dev) - Documentation Verification Agent*
"""

    return body
