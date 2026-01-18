from typing import List, Dict, Any, Tuple
from datetime import datetime

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

    total_matches = len(matches)
    print(f"\n{'='*80}")
    print(f"🔍 Starting comparison of {total_matches} function pairs...")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    for idx, (code_func, doc_func) in enumerate(matches, 1):
        if code_func is None:
            func_name = doc_func.name
            status_msg = f"⚠️  [{idx}/{total_matches}] {datetime.now().strftime('%H:%M:%S')} - Documented but not in code: {func_name}"
            print(status_msg)
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
            func_name = code_func.name
            status_msg = f"📝 [{idx}/{total_matches}] {datetime.now().strftime('%H:%M:%S')} - Code but not documented: {func_name}"
            print(status_msg)
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
            func_name = f"{code_func.name} ↔ {doc_func.name}"
            status_msg = f"🔍 [{idx}/{total_matches}] {datetime.now().strftime('%H:%M:%S')} - Comparing: {func_name}"
            print(status_msg)
            
            # Perform hybrid or LLM-only comparison
            if use_hybrid:
                result = comparator.compare(code_func, doc_func)
                methods_used.append(result.method)
                method_display = {
                    'embedding_only': '⚡ (embedding-only)',
                    'hybrid': '🤖⚡ (hybrid: embedding + LLM)',
                    'llm_only': '🤖 (LLM-only)'
                }.get(result.method, f'({result.method})')
                print(f"   └─ Method: {method_display}, Confidence: {result.confidence}%, Embedding: {result.embedding_score:.2f}")
                # Convert to ComparisonResult for compatibility
                from app.comparison.engine import ComparisonResult
                result_comp = ComparisonResult(
                    matches=result.matches,
                    confidence=result.confidence,
                    issues=result.issues
                )
            else:
                print(f"   └─ Method: 🤖 (LLM-only)")
                result_comp = comparator.compare(code_func, doc_func)
                methods_used.append("llm_only")
                print(f"   └─ Confidence: {result_comp.confidence}%")
            
            confidence = result_comp.confidence
            
            # Consider verified if confidence >= 80 (semantic equivalence)
            if confidence >= 80:
                verified += 1
            else:
                # Only report issues if confidence is below threshold
                all_issues.extend(result_comp.issues)
            
            confidence_scores.append(confidence)
            total_confidence += confidence

    print(f"\n{'='*80}")
    print(f"✅ Completed comparison of {total_matches} function pairs")
    print(f"📅 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

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
