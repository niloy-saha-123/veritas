"""AI comparison layer for Veritas - ML-enhanced semantic analysis."""

from app.comparison.engine import GeminiComparator, ComparisonResult, Issue
from app.comparison.hybrid_engine import HybridComparator, HybridComparisonResult
from app.comparison.semantic_matcher import SemanticMatcher, SimilarityScore
from app.comparison.scorer import analyze_repository, match_functions

__all__ = [
    "GeminiComparator",
    "ComparisonResult",
    "Issue",
    "HybridComparator",
    "HybridComparisonResult",
    "SemanticMatcher",
    "SimilarityScore",
    "analyze_repository",
    "match_functions",
]
