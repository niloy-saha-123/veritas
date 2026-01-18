#!/usr/bin/env python3
"""Test API with three scenarios: perfect match, complete mismatch, and partial match."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

import requests
import json

# ============================================================================
# SCENARIO 1: PERFECT MATCH - Code and docs are perfectly aligned
# ============================================================================
perfect_match_code = """
def add_numbers(a: int, b: int) -> int:
    \"\"\"
    Add two integers together.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Sum of a and b
    \"\"\"
    return a + b

def greet_user(name: str, greeting: str = "Hello") -> str:
    \"\"\"
    Greet a user with a custom message.
    
    Args:
        name: Name of the user
        greeting: Greeting message (default: "Hello")
    
    Returns:
        Greeting message
    \"\"\"
    return f"{greeting}, {name}!"
"""

perfect_match_docs = """
## add_numbers

Add two integers together.

### Parameters
- `a` (int): First integer
- `b` (int): Second integer

### Returns
- `int`: Sum of a and b

## greet_user

Greet a user with a custom message.

### Parameters
- `name` (str): Name of the user
- `greeting` (str): Greeting message (default: "Hello")

### Returns
- `str`: Greeting message
"""

# ============================================================================
# SCENARIO 2: COMPLETE MISMATCH - Code and docs are completely different
# ============================================================================
mismatch_code = """
def calculate_total(price: float, quantity: int, discount: float = 0.1) -> float:
    \"\"\"
    Calculate total with discount.
    \"\"\"
    return (price * quantity) * (1 - discount)

def process_payment(amount: float, currency: str = "USD") -> bool:
    \"\"\"
    Process a payment.
    \"\"\"
    return True
"""

mismatch_docs = """
## calculate_sum

Calculate the sum of two numbers.

### Parameters
- `x` (int): First number
- `y` (int): Second number

### Returns
- `int`: Sum of x and y

## send_email

Send an email to a recipient.

### Parameters
- `to` (str): Email address
- `subject` (str): Email subject

### Returns
- `bool`: Success status
"""

# ============================================================================
# SCENARIO 3: PARTIAL MATCH - Some parts match, some don't
# ============================================================================
partial_match_code = """
def get_user_info(user_id: int, include_email: bool = False) -> dict:
    \"\"\"
    Get user information by ID.
    
    Args:
        user_id: Unique user identifier
        include_email: Whether to include email address
    
    Returns:
        Dictionary containing user information
    \"\"\"
    return {"id": user_id, "name": "John"}

def delete_item(item_id: str, force: bool = False) -> bool:
    \"\"\"
    Delete an item from the database.
    
    Args:
        item_id: Item identifier
        force: Force deletion without confirmation
    
    Returns:
        True if successful
    \"\"\"
    return True
"""

partial_match_docs = """
## get_user_info

Get user information by ID.

### Parameters
- `user_id` (int): Unique user identifier
- `include_email` (bool): Whether to include email address
- `include_avatar` (bool): Whether to include avatar URL  # EXTRA: not in code

### Returns
- `dict`: Dictionary containing user information

## delete_item

Remove an item from the system.

### Parameters
- `item_id` (str): Item identifier
# MISSING: force parameter is not documented

### Returns
- `bool`: True if successful
"""


def test_scenario(name: str, code: str, docs: str, expected_trust_min: int = None, expected_trust_max: int = None):
    """Test a single scenario."""
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/v1/analyze"
    
    payload = {
        "code_content": code,
        "doc_content": docs,
        "language": "python"
    }
    
    print("\n" + "=" * 70)
    print(f"SCENARIO: {name}")
    print("=" * 70)
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ ERROR: Status {response.status_code}")
            print(response.text)
            return
        
        result = response.json()
        trust_score = result.get('metadata', {}).get('trust_score', 0)
        discrepancies = result.get('discrepancies', [])
        
        print(f"\n✅ Trust Score: {trust_score}%")
        print(f"📊 Total Functions: {result.get('metadata', {}).get('total_functions', 0)}")
        print(f"✅ Verified: {result.get('metadata', {}).get('verified', 0)}")
        print(f"⚠️  Discrepancies: {len(discrepancies)}")
        
        if expected_trust_min is not None:
            if expected_trust_min <= trust_score <= (expected_trust_max or 100):
                print(f"✅ Trust score in expected range [{expected_trust_min}-{expected_trust_max or 100}%]")
            else:
                print(f"⚠️  Trust score {trust_score}% outside expected range [{expected_trust_min}-{expected_trust_max or 100}%]")
        
        if discrepancies:
            print(f"\n📋 Discrepancies Found:")
            for i, disc in enumerate(discrepancies[:10], 1):  # Show first 10
                severity = disc.get('severity', 'unknown').upper()
                desc = disc.get('description', '')[:80]  # Truncate long descriptions
                print(f"  {i}. [{severity}] {desc}")
            
            if len(discrepancies) > 10:
                print(f"  ... and {len(discrepancies) - 10} more")
        else:
            print("\n✨ No discrepancies found - perfect match!")
        
        print(f"\n📝 Summary: {result.get('summary', 'N/A')}")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server.")
        print("   Make sure the FastAPI server is running:")
        print("   cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all test scenarios."""
    print("=" * 70)
    print("VERITAS API TEST - THREE SCENARIOS")
    print("=" * 70)
    print("\nTesting /api/v1/analyze endpoint with:")
    print("  1. Perfect Match - Code and docs are perfectly aligned")
    print("  2. Complete Mismatch - Code and docs are completely different")
    print("  3. Partial Match - Some parts match, some don't")
    
    # Scenario 1: Perfect Match - Should have high trust score (80-100%)
    test_scenario(
        "1. PERFECT MATCH",
        perfect_match_code,
        perfect_match_docs,
        expected_trust_min=80,
        expected_trust_max=100
    )
    
    # Scenario 2: Complete Mismatch - Should have low trust score (0-20%)
    test_scenario(
        "2. COMPLETE MISMATCH",
        mismatch_code,
        mismatch_docs,
        expected_trust_min=0,
        expected_trust_max=20
    )
    
    # Scenario 3: Partial Match - Should have medium trust score (40-70%)
    test_scenario(
        "3. PARTIAL MATCH",
        partial_match_code,
        partial_match_docs,
        expected_trust_min=40,
        expected_trust_max=70
    )
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
