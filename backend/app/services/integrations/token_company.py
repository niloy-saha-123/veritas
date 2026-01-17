# Token Company API integration - compresses prompts before sending to LLMs

"""Token Company Integration Service"""

from typing import Dict, Any
import os
import sys

if __name__ == "__main__" and __package__ is None:
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    sys.path.insert(0, backend_root)

from app.core.config import settings

try:
    from tokenc import TokenClient
except Exception:  # pragma: no cover - optional dependency
    TokenClient = None


class TokenCompanyClient:
    """Client for Token Company prompt compression."""

    def __init__(self):
        self.api_key = settings.TOKEN_COMPANY_API_KEY
        self._client = TokenClient(api_key=self.api_key) if self.api_key and TokenClient else None

    def compress_input(self, input_text: str, aggressiveness: float = 0.8) -> Dict[str, Any]:
        """
        Compress input text to reduce tokens before sending to LLM.

        Args:
            input_text: Text to compress
            aggressiveness: 0.0-1.0, higher = more compression

        Returns:
            Dict with compressed output and metadata. Falls back to original text
            if the SDK isn't available or compression fails.
        """
        if not self._client:
            return {
                "output": input_text,
                "compressed": False,
                "reason": "token_company_unavailable",
            }

        try:
            result = self._client.compress_input(input=input_text, aggressiveness=aggressiveness)
            return {
                "output": getattr(result, "output", input_text),
                "compressed": True,
                "original_tokens": getattr(result, "original_tokens", None),
                "compressed_tokens": getattr(result, "compressed_tokens", None),
            }
        except Exception as exc:
            return {
                "output": input_text,
                "compressed": False,
                "reason": "token_company_error",
                "error": str(exc),
            }


if __name__ == "__main__":
    sample_text = "Summarize the function parameters and return type."
    client = TokenCompanyClient()
    result = client.compress_input(sample_text, aggressiveness=0.8)
    print("compressed:", result.get("compressed"))
    print("output:", result.get("output"))
