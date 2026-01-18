from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json
import time
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
        # Build detailed parameter information
        code_params_detail = []
        for p in code_func.parameters:
            param_str = p.name
            if p.type:
                param_str += f": {p.type}"
            if p.default:
                param_str += f" = {p.default}"
            code_params_detail.append(f"  - {param_str}")
        
        doc_params_detail = []
        for p in doc_func.parameters:
            param_str = p.name
            if p.type:
                param_str += f" ({p.type})"
            doc_params_detail.append(f"  - {param_str}")

        return f"""
Perform a SEMANTIC analysis comparing a Python function's code signature with its documentation. Focus on functional equivalence and meaning, not exact string matching.

TASK: Determine if the code and documentation represent the SAME FUNCTION semantically, even if:
- Parameter names are slightly different but mean the same thing
- Documentation style differs (formal vs casual)
- Minor documentation gaps exist (missing optional details)
- Type hints vs documentation formats differ

ACTUAL CODE:
Function Name: {code_func.name}
Parameters:
{chr(10).join(code_params_detail) if code_params_detail else "  - (no parameters)"}
Return Type: {code_func.return_type or 'not specified'}
Docstring: {code_func.docstring[:500] if code_func.docstring else 'none'}

DOCUMENTATION:
Function Name: {doc_func.name}
Parameters:
{chr(10).join(doc_params_detail) if doc_params_detail else "  - (no parameters mentioned)"}
Return Type: {doc_func.return_type or 'not specified'}
Docstring: {doc_func.docstring[:500] if doc_func.docstring else 'none'}

ANALYSIS INSTRUCTIONS:
1. Are these the SAME function semantically? Consider:
   - Function purpose and behavior
   - Parameter semantics (does "price" match "cost"? does "discount" match "tax_rate"?)
   - Required vs optional parameters
   - Return value meaning

2. Only report CRITICAL mismatches that would cause user confusion or errors:
   - Missing REQUIRED parameters (users would get runtime errors)
   - Completely wrong parameter types that would cause errors
   - Missing critical functionality described in docs
   - Return type mismatches that break expectations

3. IGNORE minor issues:
   - Missing type hints in documentation (if code has them)
   - Documentation style differences
   - Missing examples or code samples
   - Minor naming variations with same meaning
   - Optional documentation details

4. Set confidence 80-100% if functions are semantically equivalent (even with minor doc gaps)
5. Set confidence 50-79% if mostly similar but has some notable differences
6. Set confidence 0-49% only if functions are fundamentally different

Respond with JSON only:
{{
  "matches": true/false,
  "confidence": 0-100,
  "semantic_analysis": "Brief explanation of semantic equivalence",
  "issues": [
    {{
      "severity": "high/medium/low",
      "issue": "description of CRITICAL problem only",
      "code_has": "what the code shows",
      "docs_say": "what docs claim",
      "suggested_fix": "how to fix it"
    }}
  ]
}}
""".strip()

    def _call_gemini(self, prompt: str, max_retries: int = 3) -> str:
        """
        Call Gemini API with retry logic for rate limits.
        
        Args:
            prompt: Prompt text to send
            max_retries: Maximum number of retry attempts (default: 3)
        
        Returns:
            Response text from Gemini API
        
        Raises:
            RuntimeError: If API key is missing
            requests.exceptions.HTTPError: If API call fails after all retries
        """
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is missing")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt}]}]}

        # Retry logic with exponential backoff for rate limits
        for attempt in range(max_retries):
            try:
                resp = requests.post(url, json=data, headers=headers, timeout=60)
                resp.raise_for_status()
                result = resp.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
            
            except requests.exceptions.HTTPError as e:
                # Check if it's a rate limit error (429)
                if e.response.status_code == 429:
                    if attempt < max_retries - 1:
                        # Exponential backoff: wait 2^attempt seconds (1s, 2s, 4s, etc.)
                        wait_time = 2 ** attempt
                        print(f"⚠️  Rate limited (429). Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        # Last attempt failed
                        print(f"❌ Rate limit exceeded after {max_retries} attempts")
                        raise requests.exceptions.HTTPError(
                            f"Rate limit exceeded. Please wait before retrying. "
                            f"Last error: {e.response.status_code} - {e.response.text}"
                        ) from e
                else:
                    # Non-rate-limit error - don't retry
                    raise
            
            except Exception as e:
                # Other errors (network, timeout, etc.) - retry with backoff
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"⚠️  API call failed: {e}. Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise
        
        # Should not reach here, but just in case
        raise RuntimeError(f"Failed to call Gemini API after {max_retries} attempts")

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
