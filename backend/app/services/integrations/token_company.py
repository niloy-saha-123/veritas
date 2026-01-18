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
    import tokenc
except Exception:  # pragma: no cover - optional dependency
    tokenc = None


class TokenCompanyClient:
    """Client for Token Company prompt compression."""

    def __init__(self):
        self.api_key = settings.TOKEN_COMPANY_API_KEY
        if self.api_key and tokenc:
            self._client = tokenc.TokenClient(api_key=self.api_key)
        else:
            self._client = None

    def compress_input(self, input_text: str, aggressiveness: float = 0.5) -> Dict[str, Any]:
        """
        Compress input text to reduce tokens before sending to LLM.
        
        Uses Token Company API to intelligently compress prompts while preserving
        semantic meaning and context. This reduces token usage and costs when
        sending prompts to LLMs like Gemini.

        Args:
            input_text: Text/prompt to compress
            aggressiveness: 0.0-1.0, compression level (default: 0.5)
                          - 0.0 = minimal compression (more context preserved)
                          - 1.0 = maximum compression (most tokens saved)
                          - 0.5 = balanced compression (good default)

        Returns:
            Dict with:
            - output: Compressed text (or original if compression failed/unavailable)
            - compressed: True if compression was applied, False otherwise
            - original_tokens: Number of tokens before compression (if available)
            - compressed_tokens: Number of tokens after compression (if available)
            - reason: Why compression wasn't applied (if not compressed)
        """
        if not self._client:
            return {
                "output": input_text,
                "compressed": False,
                "reason": "token_company_unavailable",
            }

        try:
            # Use Token Company API as per official documentation
            response = self._client.compress_input(
                input=input_text,
                aggressiveness=aggressiveness,
            )
            
            # Access response.output directly (as per Token Company API)
            compressed_output = response.output
            
            # Extract metadata if available
            original_tokens = getattr(response, "original_tokens", None)
            compressed_tokens = getattr(response, "compressed_tokens", None)
            
            return {
                "output": compressed_output,
                "compressed": True,
                "original_tokens": original_tokens,
                "compressed_tokens": compressed_tokens,
            }
        except Exception as exc:
            # Fallback to original text if compression fails
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
