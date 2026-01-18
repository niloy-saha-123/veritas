# ML-Enhanced Comparison Engine

## Overview

The Veritas comparison engine uses a sophisticated **hybrid ML approach** combining:
1. **Embedding-based semantic similarity** (fast, cheap) - Uses Sentence Transformers
2. **LLM semantic analysis** (accurate, expensive) - Uses Google Gemini with Token Company compression
3. **Feature engineering** (robust matching) - Parameter types, return types, docstrings

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    analyze_repository()                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              SemanticMatcher.find_best_matches()            │
│  - Embedding-based similarity (Sentence Transformers)       │
│  - Name similarity (Levenshtein distance)                   │
│  - Feature similarity (parameters, types, docstrings)       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              HybridComparator.compare()                     │
│                                                              │
│  High similarity (>0.85):                                   │
│    └─> Embedding only (fast, no LLM call)                  │
│                                                              │
│  Medium similarity (0.6-0.85):                              │
│    └─> Hybrid: 40% embedding + 60% LLM                     │
│                                                              │
│  Low similarity (<0.6):                                     │
│    └─> LLM focused: 20% embedding + 80% LLM                │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. SemanticMatcher (`semantic_matcher.py`)

Uses **Sentence Transformers** (all-MiniLM-L6-v2) for fast semantic similarity.

**Features:**
- Embedding-based cosine similarity
- Name similarity (Levenshtein distance)
- Feature-based similarity (parameter count, types, docstrings)
- Weighted combination of all methods

**Usage:**
```python
from app.comparison.semantic_matcher import SemanticMatcher

matcher = SemanticMatcher()
similarity = matcher.compute_similarity(code_func, doc_func)
# similarity.score: 0.0-1.0
# similarity.method: 'hybrid_embedding' or 'hybrid_fallback'
# similarity.confidence: 0.0-1.0
```

### 2. HybridComparator (`hybrid_engine.py`)

Combines embeddings with LLM analysis for optimal accuracy and cost.

**Strategy:**
- **High similarity (>0.85)**: Trust embeddings, skip expensive LLM call
- **Medium similarity (0.6-0.85)**: Use hybrid (40% embedding + 60% LLM)
- **Low similarity (<0.6)**: Use LLM-focused (20% embedding + 80% LLM)

**Benefits:**
- ⚡ Fast for high-similarity cases (no LLM needed)
- 💰 Cost-effective (only uses LLM when needed)
- 🎯 Accurate (LLM for edge cases)

### 3. GeminiComparator (`engine.py`)

LLM-based semantic analysis using Google Gemini with Token Company compression.

**Features:**
- Semantic understanding (not just string matching)
- Critical issue detection (focuses on user-impacting problems)
- Confidence scoring (0-100%)
- Token compression (reduces API costs)

## Performance Characteristics

| Method | Speed | Cost | Accuracy | Use Case |
|--------|-------|------|----------|----------|
| Embedding Only | ⚡⚡⚡ Fast | 💰💰💰 Low | 🎯 Good | High similarity (>0.85) |
| Hybrid | ⚡⚡ Medium | 💰💰 Medium | 🎯 Excellent | Medium similarity (0.6-0.85) |
| LLM Only | ⚡ Slow | 💰 High | 🎯 Excellent | Low similarity (<0.6) or complex cases |

## Trust Score Calculation

The trust score is calculated as the **average confidence** across all function comparisons:

```
trust_score = (sum of all confidence scores) / (total functions)
```

**Confidence thresholds:**
- **≥80%**: Verified (functions match semantically)
- **50-79%**: Partial match (some issues detected)
- **<50%**: Mismatch (significant differences)

## ML Model Details

### Sentence Transformer Model: `all-MiniLM-L6-v2`

- **Size**: 22.7 MB
- **Dimensions**: 384
- **Speed**: ~6,000 sentences/sec on CPU
- **Accuracy**: Good for semantic similarity tasks
- **Lazy loading**: Model loads on first use

### Fine-tuning Potential

The system is designed to support fine-tuning on code-doc pairs:
- Train on labeled code-doc matching datasets
- Improve parameter matching accuracy
- Better understanding of code semantics

## Configuration

You can adjust thresholds in `hybrid_engine.py`:

```python
self.embedding_threshold_high = 0.85   # Above: use embedding only
self.embedding_threshold_medium = 0.60 # Between: use hybrid
```

## Future Enhancements

1. **Fine-tuned embeddings**: Train on code-doc pairs for better accuracy
2. **Confidence calibration**: Use ML to better calibrate confidence scores
3. **Parameter matching**: ML model for parameter-level matching
4. **Type inference**: Better understanding of type compatibility
5. **Historical learning**: Learn from past comparisons to improve accuracy

## Dependencies

```txt
sentence-transformers>=2.2.0  # For embeddings
numpy>=1.24.0                  # For similarity calculations
scikit-learn>=1.3.0            # For ML utilities (future)
google-genai>=0.2.2            # For LLM analysis
tokenc>=0.1.0                  # For prompt compression
```
