"""
Semantic Matching Engine using Embeddings
Uses sentence transformers for fast semantic similarity computation
"""

from typing import List, Tuple, Dict, Optional
import numpy as np
from dataclasses import dataclass

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: sentence-transformers not installed. Using fallback similarity.")

from app.models.function_signature import FunctionSignature, Parameter


@dataclass
class SimilarityScore:
    """Similarity score between two functions."""
    score: float  # 0-1 similarity score
    method: str  # 'embedding', 'name', 'feature'
    confidence: float  # Confidence in the match


class SemanticMatcher:
    """
    ML-based semantic matcher using embeddings for function similarity.
    Combines multiple features for robust matching.
    """
    
    def __init__(self):
        self.encoder = None
        if EMBEDDINGS_AVAILABLE:
            try:
                # Use a lightweight, fast model optimized for similarity
                # all-MiniLM-L6-v2 is small, fast, and good for semantic similarity
                self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Loaded semantic embedding model: all-MiniLM-L6-v2")
            except Exception as e:
                print(f"⚠️  Could not load embedding model: {e}")
                self.encoder = None
    
    def _encode_function(self, func: FunctionSignature) -> str:
        """Convert function signature to a text representation for embedding."""
        parts = []
        
        # Function name and purpose
        parts.append(f"Function: {func.name}")
        
        # Parameters
        if func.parameters:
            param_strs = []
            for p in func.parameters:
                param_desc = p.name
                if p.type:
                    param_desc += f" ({p.type})"
                if p.default:
                    param_desc += f" default {p.default}"
                param_strs.append(param_desc)
            parts.append(f"Parameters: {', '.join(param_strs)}")
        else:
            parts.append("Parameters: none")
        
        # Return type
        if func.return_type:
            parts.append(f"Returns: {func.return_type}")
        
        # Docstring (truncated for efficiency)
        if func.docstring:
            doc_summary = func.docstring[:200].replace('\n', ' ')
            parts.append(f"Purpose: {doc_summary}")
        
        return ". ".join(parts)
    
    def compute_similarity(
        self, 
        func1: FunctionSignature, 
        func2: FunctionSignature
    ) -> SimilarityScore:
        """
        Compute semantic similarity between two functions.
        Returns similarity score (0-1) and confidence.
        """
        # Method 1: Name similarity (fast fallback)
        name_score = self._name_similarity(func1.name, func2.name)
        
        # Method 2: Feature-based similarity
        feature_score = self._feature_similarity(func1, func2)
        
        # Method 3: Embedding-based similarity (if available)
        embedding_score = None
        if self.encoder is not None:
            try:
                embedding_score = self._embedding_similarity(func1, func2)
            except Exception as e:
                print(f"⚠️  Embedding similarity failed: {e}")
        
        # Combine scores with weights
        if embedding_score is not None:
            # Weighted combination: embedding (60%), name (20%), features (20%)
            final_score = (
                0.6 * embedding_score +
                0.2 * name_score +
                0.2 * feature_score
            )
            method = "hybrid_embedding"
            confidence = 0.9
        else:
            # Fallback: name (50%) + features (50%)
            final_score = 0.5 * name_score + 0.5 * feature_score
            method = "hybrid_fallback"
            confidence = 0.7
        
        return SimilarityScore(
            score=final_score,
            method=method,
            confidence=confidence
        )
    
    def _embedding_similarity(
        self, 
        func1: FunctionSignature, 
        func2: FunctionSignature
    ) -> float:
        """Compute cosine similarity using embeddings."""
        text1 = self._encode_function(func1)
        text2 = self._encode_function(func2)
        
        embeddings = self.encoder.encode([text1, text2])
        
        # Compute cosine similarity
        dot_product = np.dot(embeddings[0], embeddings[1])
        norm1 = np.linalg.norm(embeddings[0])
        norm2 = np.linalg.norm(embeddings[1])
        
        similarity = dot_product / (norm1 * norm2)
        
        # Normalize to 0-1 range (cosine similarity is -1 to 1)
        return max(0, (similarity + 1) / 2)
    
    def _normalize_name(self, name: str) -> str:
        """Normalize function name to handle camelCase, snake_case, etc."""
        import re
        # Convert camelCase to snake_case
        # e.g., "calculateFactorial" -> "calculate_factorial"
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        normalized = s2.lower().replace('_', ' ')
        return normalized
    
    def _name_similarity(self, name1: str, name2: str) -> float:
        """Compute name similarity using edit distance and common patterns."""
        name1_lower = name1.lower()
        name2_lower = name2.lower()
        
        # Exact match
        if name1_lower == name2_lower:
            return 1.0
        
        # Normalize names (camelCase -> snake_case -> words)
        norm1 = self._normalize_name(name1)
        norm2 = self._normalize_name(name2)
        
        # Check if normalized names match
        if norm1 == norm2:
            return 0.95  # Very high similarity (same words, different format)
        
        # Check for common words (e.g., "calculate factorial" vs "calc factorial")
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        if words1 and words2:
            common = len(words1 & words2)
            total = len(words1 | words2)
            if total > 0:
                jaccard = common / total
                # If most words match, give high similarity
                if jaccard >= 0.7:
                    return 0.85  # High similarity
                elif jaccard >= 0.5:
                    return 0.70  # Good similarity
                elif jaccard > 0.3:
                    return 0.50  # Moderate similarity
        
        # Levenshtein distance (simple approximation)
        return self._levenshtein_similarity(name1_lower, name2_lower)
    
    def _levenshtein_similarity(self, s1: str, s2: str) -> float:
        """Simple Levenshtein-based similarity."""
        if not s1 or not s2:
            return 0.0
        
        if len(s1) > len(s2):
            s1, s2 = s2, s1
        
        distances = list(range(len(s1) + 1))
        for i2, c2 in enumerate(s2):
            new_distances = [i2 + 1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    new_distances.append(distances[i1])
                else:
                    new_distances.append(1 + min(
                        distances[i1],
                        distances[i1 + 1],
                        new_distances[-1]
                    ))
            distances = new_distances
        
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0
        
        distance = distances[-1]
        similarity = 1 - (distance / max_len)
        return max(0.0, similarity)
    
    def _feature_similarity(
        self, 
        func1: FunctionSignature, 
        func2: FunctionSignature
    ) -> float:
        """Compute similarity based on function features."""
        scores = []
        
        # Parameter count similarity
        params1 = len(func1.parameters)
        params2 = len(func2.parameters)
        if params1 > 0 or params2 > 0:
            param_score = 1 - abs(params1 - params2) / max(params1, params2, 1)
            scores.append(param_score * 0.3)
        
        # Return type similarity
        if func1.return_type and func2.return_type:
            ret_score = 1.0 if func1.return_type == func2.return_type else 0.5
            scores.append(ret_score * 0.2)
        elif not func1.return_type and not func2.return_type:
            scores.append(1.0 * 0.2)
        else:
            scores.append(0.5 * 0.2)
        
        # Parameter type similarity
        if func1.parameters and func2.parameters:
            type_matches = 0
            total_params = max(len(func1.parameters), len(func2.parameters))
            
            # Match parameters by position
            min_len = min(len(func1.parameters), len(func2.parameters))
            for i in range(min_len):
                p1 = func1.parameters[i]
                p2 = func2.parameters[i]
                if p1.type and p2.type and p1.type == p2.type:
                    type_matches += 1
            
            type_score = type_matches / total_params if total_params > 0 else 0.5
            scores.append(type_score * 0.3)
        else:
            scores.append(0.5 * 0.3)
        
        # Docstring similarity (simple keyword overlap)
        if func1.docstring and func2.docstring:
            words1 = set(func1.docstring.lower().split())
            words2 = set(func2.docstring.lower().split())
            if words1 and words2:
                common = len(words1 & words2)
                total = len(words1 | words2)
                doc_score = common / total if total > 0 else 0.5
                scores.append(doc_score * 0.2)
            else:
                scores.append(0.5 * 0.2)
        else:
            scores.append(0.5 * 0.2)
        
        return sum(scores)
    
    def find_best_matches(
        self,
        code_functions: List[FunctionSignature],
        doc_functions: List[FunctionSignature],
        threshold: float = 0.5
    ) -> List[Tuple[Optional[FunctionSignature], Optional[FunctionSignature], SimilarityScore]]:
        """
        Find best matching functions using semantic similarity.
        Returns list of (code_func, doc_func, similarity_score) tuples.
        """
        matches = []
        used_doc_indices = set()
        
        # First, try exact name matches
        doc_map = {d.name.lower(): (i, d) for i, d in enumerate(doc_functions)}
        
        for code_func in code_functions:
            doc_idx, doc_func = doc_map.get(code_func.name.lower(), (None, None))
            
            if doc_func:
                # Exact name match - high confidence
                similarity = SimilarityScore(score=1.0, method="exact_name", confidence=1.0)
                matches.append((code_func, doc_func, similarity))
                if doc_idx is not None:
                    used_doc_indices.add(doc_idx)
            else:
                # No exact match - find best semantic match
                best_match = None
                best_score = SimilarityScore(score=0.0, method="none", confidence=0.0)
                best_idx = None
                
                for i, doc_func in enumerate(doc_functions):
                    if i in used_doc_indices:
                        continue
                    
                    similarity = self.compute_similarity(code_func, doc_func)
                    if similarity.score > best_score.score:
                        best_score = similarity
                        best_match = doc_func
                        best_idx = i
                
                # Only match if similarity is above threshold
                if best_match and best_score.score >= threshold:
                    matches.append((code_func, best_match, best_score))
                    if best_idx is not None:
                        used_doc_indices.add(best_idx)
                else:
                    # No good match found
                    matches.append((code_func, None, SimilarityScore(score=0.0, method="none", confidence=0.0)))
        
        # Add unmatched documentation functions
        for i, doc_func in enumerate(doc_functions):
            if i not in used_doc_indices:
                matches.append((None, doc_func, SimilarityScore(score=0.0, method="unmatched", confidence=0.0)))
        
        return matches
