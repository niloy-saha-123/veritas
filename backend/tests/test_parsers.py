# Test script for parsers - run from nexhacks/ with: cd backend && python tests/test_parsers.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.parsers.parser_factory import parse_code, get_supported_extensions

# Test samples for each language
java_code = '''
public class UserService {
    /**
     * Get user by ID
     */
    public User getUser(int id) {
        return null;
    }
    
    public void saveUser(User user, boolean notify) {
        // save
    }
}
'''

markdown_code = '''
# API Reference

Use `getUserById(id)` to fetch a user.

```python
def hello(name):
    return f"Hello {name}"
```
'''

json_code = '''
{
    "openapi": "3.0.0",
    "paths": {
        "/users": {
            "get": {
                "operationId": "getUsers",
                "summary": "Get all users",
                "parameters": [{"name": "limit", "in": "query"}]
            }
        }
    }
}
'''

javascript_code = '''
function fetchUser(id) {
    return fetch(`/api/users/${id}`);
}

const processData = async (data, options) => {
    return data;
};
'''

typescript_code = '''
function greet(name: string): string {
    return `Hello ${name}`;
}

async function fetchData(url: string): Promise<Response> {
    return fetch(url);
}
'''

python_code = '''
def calculate(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

async def fetch_user(user_id: str) -> dict:
    """Fetch user from database."""
    pass
'''


def run_tests():
    print("=" * 60)
    print("PARSER TESTS")
    print("=" * 60)
    print(f"\nSupported: {get_supported_extensions()}\n")
    
    tests = [
        ("Java", "UserService.java", java_code),
        ("Markdown", "README.md", markdown_code),
        ("JSON", "openapi.json", json_code),
        ("JavaScript", "app.js", javascript_code),
        ("TypeScript", "app.ts", typescript_code),
        ("Python", "utils.py", python_code),
    ]
    
    for name, filename, code in tests:
        print("-" * 40)
        print(f"Testing {name} Parser ({filename})")
        print("-" * 40)
        results = parse_code(filename, code)
        if results:
            for func in results:
                params = ', '.join(p.name for p in func.parameters)
                prefix = "async " if hasattr(func, 'is_async') and func.is_async else ""
                print(f"  {prefix}{func.name}({params})")
            print(f"  [OK] {len(results)} found\n")
        else:
            print(f"  [SKIP] Parser not implemented or no results\n")
    
    print("=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
