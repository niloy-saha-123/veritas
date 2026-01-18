from typing import List, Dict, Any, Tuple

from app.models.function_signature import FunctionSignature
from app.comparison.engine import GeminiComparator, Issue


def match_functions(
    code_functions: List[FunctionSignature],
    doc_functions: List[FunctionSignature],
) -> List[Tuple[FunctionSignature | None, FunctionSignature | None]]:
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
) -> Dict[str, Any]:
    comparator = GeminiComparator()
    matches = match_functions(code_functions, doc_functions)

    all_issues: List[Issue] = []
    verified = 0

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
        elif doc_func is None:
            all_issues.append(Issue(
                severity="low",
                function=code_func.name,
                issue="Function exists in code but is not documented",
                code_has=f"{code_func.name}({', '.join(p.name for p in code_func.parameters)})",
                docs_say="No documentation found",
                suggested_fix="Add documentation for this function",
            ))
        else:
            result = comparator.compare(code_func, doc_func)
            if result.matches:
                verified += 1
            else:
                all_issues.extend(result.issues)

    total = len(matches)
    trust_score = int((verified / total) * 100) if total > 0 else 100

    return {
        "trust_score": trust_score,
        "total_functions": total,
        "verified": verified,
        "issues": [i.to_dict() for i in all_issues],
    }
