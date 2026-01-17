import sys
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent  # tests/
backend_dir = current_dir.parent      # backend/
sys.path.insert(0, str(backend_dir))

# Now import should work
from app.parsers import parse_code, is_supported_language
from app.models.function_signature import FunctionSignature, Parameter


def test_python_basic():
    """Test basic Python function parsing"""
    print("\n=== TEST 1: Python Basic Functions ===")
    
    code = """
def greet(name):
    return f"Hello {name}"

def add(a, b):
    return a + b
"""
    
    functions = parse_code(code, "test.py")
    
    assert len(functions) == 2
    assert functions[0].name == "greet"
    assert functions[1].name == "add"
    assert len(functions[0].parameters) == 1
    assert len(functions[1].parameters) == 2
    
    print("✅ Basic Python parsing works!")
    for func in functions:
        print(f"  Found: {func.name}({', '.join(p.name for p in func.parameters)})")


def test_python_with_types():
    """Test Python with type annotations"""
    print("\n=== TEST 2: Python With Type Hints ===")
    
    code = """
def authenticate(email: str, password: str, mfa_token: str = None) -> bool:
    '''Authenticate a user with email and password'''
    return True

def get_user(user_id: int) -> dict:
    '''Get user by ID'''
    return {}

async def update_profile(user_id: int, data: dict) -> dict:
    '''Update user profile'''
    return data
"""
    
    functions = parse_code(code, "auth.py")
    
    assert len(functions) == 3, f"Expected 3 functions, got {len(functions)}"
    
    # Test first function - authenticate
    auth_func = functions[0]
    assert auth_func.name == "authenticate"
    assert len(auth_func.parameters) == 3
    assert auth_func.parameters[0].name == "email"
    assert auth_func.parameters[0].type == "str"
    assert auth_func.parameters[1].name == "password"
    assert auth_func.parameters[1].type == "str"
    assert auth_func.parameters[2].name == "mfa_token"
    assert auth_func.parameters[2].default == "None"
    assert auth_func.return_type == "bool"
    assert auth_func.docstring == "Authenticate a user with email and password"
    
    # Test second function - get_user
    get_user_func = functions[1]
    assert get_user_func.name == "get_user"
    assert get_user_func.return_type == "dict"
    
    print("✅ Python type hints parsing works!")
    for func in functions:
        params_str = ', '.join(
            f"{p.name}: {p.type}" if p.type else p.name 
            for p in func.parameters
        )
        print(f"  {func.name}({params_str}) -> {func.return_type}")


def test_javascript_basic():
    """Test basic JavaScript function parsing"""
    print("\n=== TEST 3: JavaScript Basic Functions ===")
    
    code = """
function greet(name) {
    return `Hello ${name}`;
}

function add(a, b) {
    return a + b;
}
"""
    
    functions = parse_code(code, "test.js")
    
    assert len(functions) == 2
    assert functions[0].name == "greet"
    assert functions[1].name == "add"
    
    print("✅ JavaScript parsing works!")
    for func in functions:
        print(f"  Found: {func.name}({', '.join(p.name for p in func.parameters)})")


def test_javascript_with_defaults():
    """Test JavaScript with default parameters"""
    print("\n=== TEST 4: JavaScript With Defaults ===")
    
    js_code = """
function login(email, password, mfaToken = null) {
    return true;
}

const getUser = (userId) => {
    return {};
}

const updateProfile = async (userId, data) => {
    return data;
}
"""
    
    functions = parse_code(js_code, "auth.js")
    
    assert len(functions) == 3, f"Expected 3 functions, got {len(functions)}"
    
    # Test first function
    login_func = functions[0]
    assert login_func.name == "login"
    assert len(login_func.parameters) == 3
    assert login_func.parameters[0].name == "email"
    assert login_func.parameters[1].name == "password"
    assert login_func.parameters[2].name == "mfaToken"
    assert login_func.parameters[2].default == "null"
    
    # Test arrow functions
    assert functions[1].name == "getUser"
    assert functions[2].name == "updateProfile"
    
    print("✅ JavaScript defaults and arrow functions work!")
    for func in functions:
        params_str = ', '.join(
            f"{p.name} = {p.default}" if p.default else p.name
            for p in func.parameters
        )
        print(f"  {func.name}({params_str})")


def test_typescript_basic():
    """Test TypeScript function parsing"""
    print("\n=== TEST 5: TypeScript With Type Annotations ===")
    
    ts_code = """
function login(email: string, password: string, mfaToken?: string): boolean {
    return true;
}

const getUser = (userId: number): User => {
    return {} as User;
}

async function updateProfile(userId: number, data: ProfileData): Promise<Profile> {
    return data;
}
"""
    
    functions = parse_code(ts_code, "auth.ts")
    
    assert len(functions) >= 2, f"Expected at least 2 functions, got {len(functions)}"
    
    # Test first function
    login_func = functions[0]
    assert login_func.name == "login"
    assert len(login_func.parameters) == 3
    assert login_func.parameters[0].name == "email"
    assert login_func.parameters[0].type == "string"
    assert login_func.parameters[1].name == "password"
    assert login_func.parameters[1].type == "string"
    assert login_func.return_type == "boolean"
    
    print("✅ TypeScript type annotations work!")
    for func in functions:
        params_str = ', '.join(
            f"{p.name}: {p.type}" if p.type else p.name 
            for p in func.parameters
        )
        return_str = f": {func.return_type}" if func.return_type else ""
        print(f"  {func.name}({params_str}){return_str}")


def test_to_dict_serialization():
    """Test FunctionSignature.to_dict() for JSON serialization"""
    print("\n=== TEST 6: JSON Serialization (to_dict) ===")
    
    code = "def calculate(x: int, y: int = 10) -> str:\n    '''Calculate something'''\n    return str(x + y)"
    functions = parse_code(code, "test.py")
    
    result = functions[0].to_dict()
    
    assert isinstance(result, dict)
    assert result["name"] == "calculate"
    assert result["return_type"] == "str"
    assert result["docstring"] == "Calculate something"
    assert len(result["parameters"]) == 2
    assert result["parameters"][0]["name"] == "x"
    assert result["parameters"][0]["type"] == "int"
    assert result["parameters"][1]["name"] == "y"
    assert result["parameters"][1]["default"] == "10"
    
    print("✅ to_dict() serialization works!")
    print(f"  Sample output: {result}")


def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n=== TEST 7: Edge Cases ===")
    
    # Test 1: Empty code
    functions = parse_code("", "empty.py")
    assert len(functions) == 0
    print("  ✅ Empty file handled")
    
    # Test 2: Syntax error (should not crash)
    bad_code = "def broken(:\n    pass"
    functions = parse_code(bad_code, "broken.py")
    assert len(functions) == 0
    print("  ✅ Syntax errors handled gracefully")
    
    # Test 3: No functions
    no_funcs = "x = 10\ny = 20"
    functions = parse_code(no_funcs, "variables.py")
    assert len(functions) == 0
    print("  ✅ Code with no functions handled")
    
    # Test 4: Unsupported file type
    functions = parse_code("some code", "test.go")
    assert len(functions) == 0
    print("  ✅ Unsupported file types handled")
    
    print("✅ All edge cases handled!")


def test_real_world_example():
    """Test with a realistic code sample"""
    print("\n=== TEST 8: Real-World Example ===")
    
    real_code = """
from typing import Optional, List

class UserService:
    def __init__(self, db):
        self.db = db
    
    async def create_user(self, email: str, password: str, role: str = "user") -> dict:
        '''Create a new user account'''
        user = await self.db.users.create(email, password, role)
        return user
    
    async def get_user_by_id(self, user_id: int) -> Optional[dict]:
        '''Retrieve user by ID'''
        return await self.db.users.find_by_id(user_id)
    
    async def list_users(self, limit: int = 100, offset: int = 0) -> List[dict]:
        '''List all users with pagination'''
        return await self.db.users.list(limit, offset)
"""
    
    functions = parse_code(real_code, "user_service.py")
    
    # Should find __init__ + 3 async methods = 4 functions
    assert len(functions) >= 3, f"Expected at least 3 functions, got {len(functions)}"
    
    print(f"✅ Found {len(functions)} methods in UserService class!")
    for func in functions:
        if func.name != "__init__":  # Skip constructor
            params_str = ', '.join(
                f"{p.name}: {p.type}" if p.type else p.name 
                for p in func.parameters
            )
            print(f"  {func.name}({params_str}) -> {func.return_type}")


def test_multi_language_detection():
    """Test that parser factory correctly detects languages"""
    print("\n=== TEST 9: Multi-Language Auto-Detection ===")
    
    assert is_supported_language("test.py") == True
    assert is_supported_language("test.js") == True
    assert is_supported_language("test.jsx") == True
    assert is_supported_language("test.ts") == True
    assert is_supported_language("test.tsx") == True
    assert is_supported_language("test.go") == False
    assert is_supported_language("test.java") == False
    
    print("✅ Language detection works!")
    print("  Supported: .py, .js, .jsx, .ts, .tsx")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 RUNNING VERITAS PARSER TESTS")
    print("="*60)
    
    try:
        test_python_basic()
        test_python_with_types()
        test_javascript_basic()
        test_javascript_with_defaults()
        test_typescript_basic()
        test_to_dict_serialization()
        test_edge_cases()
        test_real_world_example()
        test_multi_language_detection()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\n✅ Python parser: WORKING")
        print("✅ JavaScript parser: WORKING")
        print("✅ TypeScript parser: WORKING")
        print("✅ Error handling: WORKING")
        print("✅ JSON serialization: WORKING")
        print("\n🚀 Ready to integrate with Person B's comparison engine!")
        
    except AssertionError as e:
        print("\n" + "="*60)
        print("❌ TEST FAILED!")
        print("="*60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)