#!/usr/bin/env python3
"""Quick syntax check for the ML-enhanced comparison system."""

import sys

def check_imports():
    """Check if all modules can be imported."""
    print("🔍 Checking imports...")
    
    try:
        print("  ✓ Checking semantic_matcher...")
        from app.comparison.semantic_matcher import SemanticMatcher
        print("    ✅ SemanticMatcher imported successfully")
        
        print("  ✓ Checking hybrid_engine...")
        from app.comparison.hybrid_engine import HybridComparator
        print("    ✅ HybridComparator imported successfully")
        
        print("  ✓ Checking scorer...")
        from app.comparison.scorer import analyze_repository, match_functions
        print("    ✅ Scorer functions imported successfully")
        
        print("\n✅ All imports successful!")
        return True
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_semantic_matcher():
    """Test semantic matcher fallback behavior."""
    print("\n🔍 Testing SemanticMatcher fallback...")
    
    try:
        from app.comparison.semantic_matcher import SemanticMatcher
        from app.models.function_signature import FunctionSignature, Parameter
        
        matcher = SemanticMatcher()
        
        # Create test functions
        func1 = FunctionSignature(
            name="add_numbers",
            parameters=[Parameter(name="a", type="int"), Parameter(name="b", type="int")],
            return_type="int",
            line_number=1,
            file_path="test.py"
        )
        
        func2 = FunctionSignature(
            name="add_numbers",
            parameters=[Parameter(name="x", type="int"), Parameter(name="y", type="int")],
            return_type="int",
            line_number=1,
            file_path="test.md"
        )
        
        similarity = matcher.compute_similarity(func1, func2)
        print(f"  ✅ Similarity: {similarity.score:.2f} (method: {similarity.method})")
        print(f"     Confidence: {similarity.confidence:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("VERITAS ML-ENHANCED COMPARISON SYSTEM - QUICK CHECK")
    print("=" * 60)
    
    success = True
    
    if not check_imports():
        success = False
    
    if success and not check_semantic_matcher():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All checks passed! System is ready.")
        print("\nTo run tests:")
        print("  1. Start the server: uvicorn app.main:app --reload")
        print("  2. Run tests: python3 test_api_scenarios.py")
    else:
        print("❌ Some checks failed. Please fix the errors above.")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
