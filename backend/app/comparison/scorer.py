from typing import List, Dict, Any, Tuple

from app.models.function_signature import FunctionSignature
from app.comparison.engine import GeminiComparator, Issue
from app.comparison.hybrid_engine import HybridComparator, to_comparison_result
from app.comparison.semantic_matcher import SemanticMatcher


def match_functions(
    code_functions: List[FunctionSignature],
    doc_functions: List[FunctionSignature],
    use_semantic_matching: bool = True,
) -> List[Tuple[FunctionSignature | None, FunctionSignature | None]]:
    """
    Match code functions with documentation functions.
    Uses semantic matching when enabled, otherwise uses simple name matching.
    """
    if use_semantic_matching and len(code_functions) > 0 and len(doc_functions) > 0:
        # Use ML-based semantic matching
        matcher = SemanticMatcher()
        matches_with_scores = matcher.find_best_matches(
            code_functions, 
            doc_functions,
            threshold=0.5  # Only match if similarity >= 0.5
        )
        # Extract just the function pairs (ignore similarity scores for now)
        matches = [(code_func, doc_func) for code_func, doc_func, _ in matches_with_scores]
        return matches
    else:
        # Fallback to simple name matching
        matches = []
        doc_map = {d.name.lower(): d for d in doc_functions}

        for code_func in code_functions:
            doc = doc_map.get(code_func.name.lower())
            matches.append((code_func, doc))

        code_names = {c.name.lower() for c in code_functions}
        for doc_func in doc_functions:
            if doc_func.name.lower() not in code_names:
                matches.append((None, doc_func))

        return matches


def analyze_repository(
    code_functions: List[FunctionSignature],
    doc_functions: List[FunctionSignature],
    use_hybrid: bool = True,
) -> Dict[str, Any]:
    """
    Analyze repository using ML-enhanced hybrid comparison.
    
    Args:
        code_functions: Functions extracted from code
        doc_functions: Functions extracted from documentation
        use_hybrid: If True, use hybrid engine (embeddings + LLM). If False, use LLM only.
    
    Returns:
        Analysis results with trust score, verified count, and issues
    """
    # Use hybrid comparator (embeddings + LLM) or LLM-only
    if use_hybrid:
        comparator = HybridComparator()
    else:
        comparator = GeminiComparator()
    
    # Use semantic matching for better function pairing
    matches = match_functions(code_functions, doc_functions, use_semantic_matching=True)

    all_issues: List[Issue] = []
    verified = 0
    confidence_scores = []
    total_confidence = 0
    methods_used = []

    for code_func, doc_func in matches:
        if code_func is None:
            all_issues.append(Issue(
                severity="medium",
                function=doc_func.name,
                issue="Documented function not found in code",
                code_has="Function does not exist",
                docs_say=f"Documents {doc_func.name}()",
                suggested_fix="Remove from documentation or check if it was renamed",
            ))
            confidence_scores.append(0)
            methods_used.append("unmatched")
        elif doc_func is None:
            all_issues.append(Issue(
                severity="low",
                function=code_func.name,
                issue="Function exists in code but is not documented",
                code_has=f"{code_func.name}({', '.join(p.name for p in code_func.parameters)})",
                docs_say="No documentation found",
                suggested_fix="Add documentation for this function",
            ))
            confidence_scores.append(0)
            methods_used.append("unmatched")
        else:
            # Perform hybrid or LLM-only comparison
            if use_hybrid:
                result = comparator.compare(code_func, doc_func)
                methods_used.append(result.method)
                # Convert to ComparisonResult for compatibility
                from app.comparison.engine import ComparisonResult
                result_comp = ComparisonResult(
                    matches=result.matches,
                    confidence=result.confidence,
                    issues=result.issues
                )
            else:
                result_comp = comparator.compare(code_func, doc_func)
                methods_used.append("llm_only")
            
            confidence = result_comp.confidence
            
            # Consider verified if confidence >= 80 (semantic equivalence)
            if confidence >= 80:
                verified += 1
            else:
                # Only report issues if confidence is below threshold
                all_issues.extend(result_comp.issues)
            
            confidence_scores.append(confidence)
            total_confidence += confidence

    total = len(matches)
    
    # Calculate trust score using average confidence
    # This gives a more nuanced score than binary matches
    if total > 0:
        avg_confidence = total_confidence / total
        trust_score = int(avg_confidence)
    else:
        trust_score = 100
    
    # Count method usage statistics
    method_stats = {}
    for method in methods_used:
        method_stats[method] = method_stats.get(method, 0) + 1

    return {
        "trust_score": trust_score,
        "total_functions": total,
        "verified": verified,
        "average_confidence": round(total_confidence / total, 1) if total > 0 else 100.0,
        "issues": [i.to_dict() for i in all_issues],
        "method_stats": method_stats,  # Statistics on which methods were used
    }
