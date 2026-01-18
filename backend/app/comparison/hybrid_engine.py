"""
Hybrid Comparison Engine
Combines ML-based embeddings with LLM semantic analysis for optimal accuracy and performance.
"""

from typing import Tuple
from dataclasses import dataclass

from app.models.function_signature import FunctionSignature
from app.comparison.engine import GeminiComparator, ComparisonResult, Issue
from app.comparison.semantic_matcher import SemanticMatcher, SimilarityScore


@dataclass
class HybridComparisonResult:
    """Result from hybrid comparison combining embeddings and LLM."""
    matches: bool
    confidence: int  # 0-100
    issues: list[Issue]
    embedding_score: float  # 0-1
    llm_confidence: int  # 0-100 (if LLM was used)
    method: str  # 'embedding_only', 'hybrid', 'llm_only'


class HybridComparator:
    """
    Hybrid comparison engine that uses:
    1. Embedding-based semantic similarity (fast, cheap)
    2. LLM semantic analysis (accurate, expensive)
    
    Strategy:
    - High embedding similarity (>0.85): Use embedding score directly
    - Medium embedding similarity (0.6-0.85): Use LLM for detailed analysis
    - Low embedding similarity (<0.6): Mark as different, use LLM only if needed
    """
    
    def __init__(self):
        self.embedding_matcher = SemanticMatcher()
        self.llm_comparator = GeminiComparator()
        self.embedding_threshold_high = 0.85  # Above this, trust embedding score
        self.embedding_threshold_medium = 0.60  # Between this and high, use LLM
        self.embedding_threshold_very_low = 0.2  # Below this, skip LLM (complete mismatch)
    
    def compare(
        self, 
        code_func: FunctionSignature, 
        doc_func: FunctionSignature
    ) -> HybridComparisonResult:
        """
        Compare two functions using hybrid approach.
        Uses embeddings for fast screening, LLM for detailed analysis when needed.
        """
        # Step 1: Compute embedding-based similarity
        similarity = self.embedding_matcher.compute_similarity(code_func, doc_func)
        embedding_score = similarity.score
        
        # Step 1.5: Check name similarity - if names are very different, skip LLM
        # This catches cases where overall similarity is medium but names are completely different
        name_similarity = self._compute_name_similarity(code_func.name, doc_func.name)
        name_threshold = 0.3  # If name similarity < 0.3, functions are too different
        
        # Step 1.6: Check for parameter mismatches - if there are mismatches, use LLM even if similarity is high
        # This catches partial matches where parameters differ
        has_param_mismatch = self._has_parameter_mismatch(code_func, doc_func)
        
        # Step 2: Decide on comparison strategy
        # Very low similarity (<0.2) OR very different names (<0.3) = complete mismatch
        if embedding_score < self.embedding_threshold_very_low or name_similarity < name_threshold:
            # Very different functions - trust embeddings, save LLM calls
            return self._embedding_only_very_low(code_func, doc_func, similarity)
        elif embedding_score >= self.embedding_threshold_high and not has_param_mismatch:
            # High similarity AND no parameter mismatches - trust embeddings, no need for expensive LLM call
            return self._embedding_only_result(code_func, doc_func, similarity)
        elif embedding_score >= self.embedding_threshold_medium:
            # Medium similarity - use LLM for detailed analysis
            return self._hybrid_comparison(code_func, doc_func, similarity)
        else:
            # Low-medium similarity (0.2-0.6) - use LLM to confirm and get detailed issues
            return self._llm_focused_comparison(code_func, doc_func, similarity)
    
    def _embedding_only_very_low(
        self,
        code_func: FunctionSignature,
        doc_func: FunctionSignature,
        similarity: SimilarityScore
    ) -> HybridComparisonResult:
        """Handle very low similarity cases (complete mismatch) - skip LLM to save API calls."""
        # Very low similarity = functions are completely different
        confidence = int(similarity.score * 100)
        
        # Create issue indicating complete mismatch
        issues = [
            Issue(
                severity="high",
                function=code_func.name,
                issue=f"Functions are completely different (embedding similarity {confidence}%). Code function '{code_func.name}' does not match documented function '{doc_func.name}'.",
                code_has=f"{code_func.name}({', '.join(p.name for p in code_func.parameters)})",
                docs_say=f"{doc_func.name}({', '.join(p.name for p in doc_func.parameters)})",
                suggested_fix="Check if functions were renamed, or if documentation refers to different code. Consider updating documentation to match actual code."
            )
        ]
        
        return HybridComparisonResult(
            matches=False,
            confidence=confidence,
            issues=issues,
            embedding_score=similarity.score,
            llm_confidence=0,  # No LLM call made
            method="embedding_only_very_low"
        )
    
    def _embedding_only_result(
        self,
        code_func: FunctionSignature,
        doc_func: FunctionSignature,
        similarity: SimilarityScore
    ) -> HybridComparisonResult:
        """Handle high-confidence embedding matches (no LLM needed)."""
        # Convert embedding score (0-1) to confidence (0-100)
        confidence = int(similarity.score * 100)
        
        # For high similarity, assume minimal issues
        # Still do a quick check for obvious mismatches
        issues = self._quick_issue_check(code_func, doc_func)
        
        return HybridComparisonResult(
            matches=confidence >= 80,
            confidence=confidence,
            issues=issues,
            embedding_score=similarity.score,
            llm_confidence=confidence,  # Not using LLM, so use embedding as proxy
            method="embedding_only"
        )
    
    def _hybrid_comparison(
        self,
        code_func: FunctionSignature,
        doc_func: FunctionSignature,
        similarity: SimilarityScore
    ) -> HybridComparisonResult:
        """Use both embeddings and LLM for medium-confidence cases."""
        # Get LLM analysis
        llm_result = self.llm_comparator.compare(code_func, doc_func)
        
        # Combine embedding and LLM scores
        # Weight: 40% embedding, 60% LLM (LLM is more accurate but we trust embeddings when high)
        embedding_confidence = int(similarity.score * 100)
        llm_confidence = llm_result.confidence
        
        # Weighted combination
        combined_confidence = int(
            0.4 * embedding_confidence + 
            0.6 * llm_confidence
        )
        
        return HybridComparisonResult(
            matches=combined_confidence >= 80,
            confidence=combined_confidence,
            issues=llm_result.issues,
            embedding_score=similarity.score,
            llm_confidence=llm_confidence,
            method="hybrid"
        )
    
    def _llm_focused_comparison(
        self,
        code_func: FunctionSignature,
        doc_func: FunctionSignature,
        similarity: SimilarityScore
    ) -> HybridComparisonResult:
        """Use LLM for detailed analysis of low-similarity cases."""
        llm_result = self.llm_comparator.compare(code_func, doc_func)
        
        # For low embedding similarity, trust LLM more (it can find semantic equivalence)
        # But don't ignore embedding completely - if embedding is very low (<0.3) and LLM is high,
        # be cautious
        embedding_confidence = int(similarity.score * 100)
        llm_confidence = llm_result.confidence
        
        if similarity.score < 0.3 and llm_confidence > 80:
            # Embedding says very different, but LLM says similar
            # Trust LLM but reduce confidence slightly
            combined_confidence = int(llm_confidence * 0.9)
        else:
            # Weight: 20% embedding, 80% LLM (LLM is more accurate)
            combined_confidence = int(
                0.2 * embedding_confidence +
                0.8 * llm_confidence
            )
        
        return HybridComparisonResult(
            matches=combined_confidence >= 80,
            confidence=combined_confidence,
            issues=llm_result.issues,
            embedding_score=similarity.score,
            llm_confidence=llm_confidence,
            method="llm_focused"
        )
    
    def _compute_name_similarity(self, name1: str, name2: str) -> float:
        """
        Compute simple name similarity to detect completely different function names.
        Returns 0-1 similarity score.
        """
        name1_lower = name1.lower()
        name2_lower = name2.lower()
        
        # Exact match
        if name1_lower == name2_lower:
            return 1.0
        
        # Check for common words (e.g., "calculate_total" vs "calculate_sum" share "calculate")
        words1 = set(name1_lower.replace('_', ' ').split())
        words2 = set(name2_lower.replace('_', ' ').split())
        
        if words1 and words2:
            common = len(words1 & words2)
            total = len(words1 | words2)
            if total > 0:
                jaccard = common / total
                if jaccard > 0.3:  # If >30% words match, might be related
                    return jaccard
        
        # If no common words or very low overlap, names are very different
        # Use simple character-based similarity as fallback
        if len(name1_lower) == 0 or len(name2_lower) == 0:
            return 0.0
        
        # Count common characters
        chars1 = set(name1_lower)
        chars2 = set(name2_lower)
        common_chars = len(chars1 & chars2)
        total_chars = len(chars1 | chars2)
        
        if total_chars == 0:
            return 0.0
        
        return common_chars / total_chars
    
    def _has_parameter_mismatch(
        self,
        code_func: FunctionSignature,
        doc_func: FunctionSignature
    ) -> bool:
        """Check if there are any parameter mismatches between code and docs."""
        code_params = {p.name.lower() for p in code_func.parameters}
        doc_params = {p.name.lower() for p in doc_func.parameters}
        
        # Check if parameter sets differ
        if code_params != doc_params:
            return True
        
        # Check if parameter counts differ
        if len(code_func.parameters) != len(doc_func.parameters):
            return True
        
        return False
    
    def _quick_issue_check(
        self,
        code_func: FunctionSignature,
        doc_func: FunctionSignature
    ) -> list[Issue]:
        """Quick check for obvious issues in high-similarity cases."""
        issues = []
        
        code_params = {p.name.lower(): p for p in code_func.parameters}
        doc_params = {p.name.lower(): p for p in doc_func.parameters}
        
        # Check for missing parameters in docs (both required and optional)
        for param_name, param in code_params.items():
            if param_name not in doc_params:
                severity = "high" if not param.default else "medium"
                param_desc = f"{param.name}: {param.type or 'Any'}"
                if param.default:
                    param_desc += f" = {param.default}"
                
                issues.append(Issue(
                    severity=severity,
                    function=code_func.name,
                    issue=f"{'Required' if not param.default else 'Optional'} parameter '{param.name}' is missing from documentation",
                    code_has=param_desc,
                    docs_say="Not documented",
                    suggested_fix=f"Add '{param.name}' parameter to documentation"
                ))
        
        # Check for extra parameters in docs that don't exist in code
        for param_name, param in doc_params.items():
            if param_name not in code_params:
                param_desc = f"{param.name}"
                if param.type:
                    param_desc += f" ({param.type})"
                
                issues.append(Issue(
                    severity="high",
                    function=code_func.name,
                    issue=f"Parameter '{param.name}' is documented but does not exist in code",
                    code_has="Parameter does not exist",
                    docs_say=param_desc,
                    suggested_fix=f"Remove '{param.name}' from documentation or check if parameter was renamed"
                ))
        
        return issues


# Adapter to convert HybridComparisonResult to ComparisonResult for compatibility
def to_comparison_result(hybrid_result: HybridComparisonResult, func_name: str) -> ComparisonResult:
    """Convert HybridComparisonResult to ComparisonResult."""
    return ComparisonResult(
        matches=hybrid_result.matches,
        confidence=hybrid_result.confidence,
        issues=hybrid_result.issues
    )
