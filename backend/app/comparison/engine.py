from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json
import requests

from app.core.config import settings
from app.models.function_signature import FunctionSignature
from app.services.integrations.token_company import TokenCompanyClient


@dataclass
class Issue:
    severity: str  # high/medium/low
    function: str
    issue: str
    code_has: str
    docs_say: str
    suggested_fix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "function": self.function,
            "issue": self.issue,
            "code_has": self.code_has,
            "docs_say": self.docs_say,
            "suggested_fix": self.suggested_fix,
        }


@dataclass
class ComparisonResult:
    matches: bool
    confidence: int
    issues: List[Issue]


class GeminiComparator:
    """Gemini-based comparison engine with Token Company compression."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = "gemini-2.5-flash"
        self.token_client = TokenCompanyClient()

    def compare(self, code_func: FunctionSignature, doc_func: FunctionSignature) -> ComparisonResult:
        prompt = self._build_prompt(code_func, doc_func)

        compressed = self.token_client.compress_input(prompt, aggressiveness=0.8)
        prompt_text = compressed.get("output", prompt)

        response_text = self._call_gemini(prompt_text)
        result = self._parse_response(response_text, code_func.name)

        return result

    def _build_prompt(self, code_func: FunctionSignature, doc_func: FunctionSignature) -> str:
        code_params = ", ".join([
            f"{p.name}: {p.type or 'Any'}" + (f" = {p.default}" if p.default else "")
            for p in code_func.parameters
        ])
        doc_params = ", ".join([p.name for p in doc_func.parameters])

        return f"""
Compare this Python function's actual code signature with its documentation.

ACTUAL CODE:
Function: {code_func.name}({code_params})
Returns: {code_func.return_type or 'not specified'}
Docstring: {code_func.docstring or 'none'}
Line: {code_func.line_number}

DOCUMENTATION:
Function: {doc_func.name}
Parameters mentioned: {doc_params or 'none'}
Return type: {doc_func.return_type or 'not specified'}
Docstring: {doc_func.docstring or 'none'}
Line: {doc_func.line_number}

Check for these issues:
1. Missing parameters (in code but not in docs)
2. Extra parameters (in docs but not in code)
3. Wrong types documented
4. Missing default values in docs
5. Incorrect return type

Respond with JSON only:
{{
  "matches": true/false,
  "confidence": 0-100,
  "issues": [
    {{
      "severity": "high/medium/low",
      "issue": "description of the problem",
      "code_has": "what the code shows",
      "docs_say": "what docs claim",
      "suggested_fix": "how to fix it"
    }}
  ]
}}
""".strip()

    def _call_gemini(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is missing")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt}]}]}

        resp = requests.post(url, json=data, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def _parse_response(self, text: str, func_name: str) -> ComparisonResult:
        start = text.find("{")
        end = text.rfind("}") + 1
        json_text = text[start:end] if start != -1 and end != -1 else "{}"

        try:
            result = json.loads(json_text)
        except Exception:
            result = {"matches": False, "confidence": 0, "issues": []}

        issues = [
            Issue(
                severity=i.get("severity", "medium"),
                function=func_name,
                issue=i.get("issue", ""),
                code_has=i.get("code_has", ""),
                docs_say=i.get("docs_say", ""),
                suggested_fix=i.get("suggested_fix", ""),
            )
            for i in result.get("issues", [])
        ]

        return ComparisonResult(
            matches=result.get("matches", False),
            confidence=int(result.get("confidence", 0)),
            issues=issues,
        )
