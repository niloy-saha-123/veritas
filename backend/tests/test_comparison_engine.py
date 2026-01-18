import os
import sys

if __name__ == "__main__" and __package__ is None:
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, backend_root)

from app.comparison.engine import GeminiComparator
from app.comparison.scorer import analyze_repository
from app.models.function_signature import FunctionSignature, Parameter


def _make_func(name: str, params: list[str]) -> FunctionSignature:
    return FunctionSignature(
        name=name,
        parameters=[Parameter(name=p) for p in params],
        return_type="str",
        docstring="test doc",
        line_number=1,
        file_path="test.py",
    )


def test_gemini_comparator_parses_json(monkeypatch):
    comparator = GeminiComparator()

    def fake_compress_input(prompt: str, aggressiveness: float = 0.8):
        return {"output": prompt, "compressed": False}

    def fake_call_gemini(prompt: str) -> str:
        return """
        {
          "matches": false,
          "confidence": 72,
          "issues": [
            {
              "severity": "high",
              "issue": "Missing parameter",
              "code_has": "login(email, password, mfa_token)",
              "docs_say": "login(email, password)",
              "suggested_fix": "Document mfa_token"
            }
          ]
        }
        """

    monkeypatch.setattr(comparator.token_client, "compress_input", fake_compress_input)
    monkeypatch.setattr(comparator, "_call_gemini", fake_call_gemini)

    code_func = _make_func("login", ["email", "password", "mfa_token"])
    doc_func = _make_func("login", ["email", "password"])

    result = comparator.compare(code_func, doc_func)
    assert result.matches is False
    assert result.confidence == 72
    assert len(result.issues) == 1
    assert result.issues[0].severity == "high"


def test_analyze_repository_trust_score(monkeypatch):
    comparator = GeminiComparator()

    def fake_compress_input(prompt: str, aggressiveness: float = 0.8):
        return {"output": prompt, "compressed": False}

    def fake_call_gemini(prompt: str) -> str:
        return '{"matches": true, "confidence": 95, "issues": []}'

    monkeypatch.setattr(comparator.token_client, "compress_input", fake_compress_input)
    monkeypatch.setattr(comparator, "_call_gemini", fake_call_gemini)

    # Monkeypatch the comparator used in analyze_repository
    monkeypatch.setattr(
        "app.comparison.scorer.GeminiComparator",
        lambda: comparator,
    )

    code_functions = [_make_func("login", ["email", "password"])]
    doc_functions = [_make_func("login", ["email", "password"])]

    result = analyze_repository(code_functions, doc_functions)
    assert result["trust_score"] == 100
    assert result["total_functions"] == 1
    assert result["verified"] == 1
    assert result["issues"] == []
