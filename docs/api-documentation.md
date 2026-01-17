# Veritas.dev API Documentation

## Overview

The Veritas.dev API provides automated documentation-code verification capabilities through a RESTful interface.

**Base URL:** `http://localhost:8000/api/v1`

**Authentication:** API key-based (coming soon)

---

## Endpoints

### Health & Status

#### GET /health

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-17T19:39:00.000Z",
  "service": "Veritas.dev API"
}
```

#### GET /status

Get detailed system status.

**Response:**
```json
{
  "status": "operational",
  "version": "1.0.0",
  "timestamp": "2024-01-17T19:39:00.000Z",
  "components": {
    "api": "healthy",
    "detection_engine": "ready",
    "integrations": "configured"
  }
}
```

---

### Analysis

#### POST /analyze

Analyze code and documentation for discrepancies.

**Request Body:**
```json
{
  "code_url": "https://github.com/user/repo",
  "doc_url": "https://docs.example.com",
  "code_content": "def hello():\n    pass",
  "doc_content": "# Documentation\n...",
  "language": "python"
}
```

**Parameters:**
- `code_url` (string, optional): URL to code repository
- `doc_url` (string, optional): URL to documentation
- `code_content` (string, optional): Raw code content
- `doc_content` (string, optional): Raw documentation content
- `language` (string, default: "python"): Programming language

**Response:**
```json
{
  "status": "success",
  "discrepancies": [
    {
      "type": "missing_documentation",
      "severity": "medium",
      "location": "file.py:42",
      "description": "Function 'calculate' is not documented",
      "code_snippet": "def calculate(x, y):",
      "doc_snippet": null,
      "suggestion": "Add documentation for function 'calculate'"
    }
  ],
  "summary": "Found 1 discrepancy",
  "timestamp": "2024-01-17T19:39:00.000Z",
  "metadata": {
    "files_analyzed": 5,
    "functions_checked": 23
  }
}
```

#### POST /analyze/upload

Upload files for analysis.

**Request:**
- Content-Type: `multipart/form-data`
- `code_file` (file, required): Source code file
- `doc_file` (file, optional): Documentation file

**Response:**
Same as `/analyze` endpoint

---

## Data Models

### DiscrepancyType

Enumeration of discrepancy types:
- `function_signature` - Function signature mismatch
- `parameter_type` - Parameter type inconsistency
- `return_type` - Return type mismatch
- `missing_documentation` - Missing documentation
- `outdated_example` - Outdated code example
- `deprecated_usage` - Deprecated function usage

### Severity Levels

- `low` - Minor issue, cosmetic
- `medium` - Should be addressed
- `high` - Important, affects usability
- `critical` - Must be fixed, breaks functionality

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Analysis failed: [error message]"
}
```

---

## Rate Limits

- **Free tier:** 100 requests/hour
- **Pro tier:** 1000 requests/hour
- **Enterprise:** Unlimited

---

## Examples

### Python Example

```python
import requests

url = "http://localhost:8000/api/v1/analyze"
data = {
    "code_content": "def add(a, b):\n    return a + b",
    "doc_content": "# add(x, y)\nAdds two numbers",
    "language": "python"
}

response = requests.post(url, json=data)
result = response.json()

print(f"Found {len(result['discrepancies'])} discrepancies")
```

### JavaScript Example

```javascript
const response = await fetch('http://localhost:8000/api/v1/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    code_content: 'function add(a, b) { return a + b; }',
    doc_content: '# add(x, y)\nAdds two numbers',
    language: 'javascript'
  })
});

const result = await response.json();
console.log(`Found ${result.discrepancies.length} discrepancies`);
```

### cURL Example

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code_content": "def multiply(a, b):\n    return a * b",
    "doc_content": "# multiply(x, y)\nMultiplies two numbers",
    "language": "python"
  }'
```

---

## Interactive Documentation

For interactive API exploration:
- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

---

## Changelog

### v1.0.0 (2024-01-17)
- Initial release
- Basic analysis endpoints
- Python code parsing
- Markdown documentation parsing
- Multi-language support foundation
