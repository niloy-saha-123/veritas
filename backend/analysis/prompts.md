# LLM Comparison Prompts

## Initial Comparison Prompt (Gemini)

This prompt is used to compare Python function signatures with their documentation.

### Prompt Template

```
Compare this Python function's actual code signature with its documentation.

ACTUAL CODE:
Function: {function_name}({parameters})
Parameters:
{parameter_details}
Return Type: {return_type}
Docstring: {docstring}
Line Number: {line_number}

DOCUMENTATION:
Function Name: {doc_function_name}
Parameters Mentioned: {doc_parameters}
Return Description: {return_description}
Code Examples: {code_examples}

Check for these mismatches:
1. Parameter names - Are all parameters in code documented? Are there extra parameters in docs?
2. Parameter types - Do the documented types match the actual type hints?
3. Default values - Are default values documented correctly?
4. Return types - Does the documented return type match the actual return type hint?
5. Missing documentation - Are there parameters or return values not mentioned in docs?
6. Outdated examples - Do code examples in docs match the actual function signature?

Respond with JSON only (no markdown, no code blocks):
{
  "matches": true/false,
  "confidence": 0-100,
  "issues": [
    {
      "severity": "high/medium/low",
      "type": "missing_parameter/wrong_type/missing_default/etc",
      "issue": "description of the problem",
      "code_has": "what the code shows",
      "docs_say": "what docs claim",
      "suggestion": "how to fix it"
    }
  ]
}
```

### Example Usage

```python
# Code function
function_name = "calculate_total"
parameters = ["price: float", "tax: float = 0.1"]
return_type = "float"
docstring = "Calculate total with tax"

# Doc function
doc_parameters = ["price", "discount"]  # Missing tax, has extra discount
return_description = "Returns the total"

# This should detect:
# - Missing parameter: tax (in code but not in docs)
# - Extra parameter: discount (in docs but not in code)
# - Missing default value documentation for tax
```

### Severity Guidelines

- **high**: Missing required parameters, wrong return type, function signature completely different
- **medium**: Wrong parameter types, missing optional parameters, missing default values
- **low**: Minor documentation inconsistencies, missing examples, formatting issues

### Notes

- Use `gemini-2.5-flash` model for fast responses
- Keep prompts concise to reduce token costs
- Always request JSON response format
- Include confidence score (0-100) for each comparison
