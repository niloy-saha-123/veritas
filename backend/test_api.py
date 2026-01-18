#!/usr/bin/env python3
"""Quick test script for the /api/v1/analyze endpoint."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

import requests
import json

# Sample Python code
sample_code = """
def calculate_total(price: float, quantity: int, discount: float = 0.0) -> float:
    '''
    Calculate the total price after discount.
    
    Args:
        price: The unit price
        quantity: Number of items
        discount: Discount percentage (0.0 to 1.0)
    
    Returns:
        Total price after discount
    '''
    return (price * quantity) * (1 - discount)

def process_order(order_id: str, items: list, shipping: bool = True):
    \"\"\"Process an order and return confirmation.\"\"\"
    return f"Order {order_id} processed with {len(items)} items"
"""

# Sample Markdown documentation (with intentional mismatch)
sample_docs = """
## calculate_total

Calculate the total price after applying a discount.

### Parameters
- `price` (float): The unit price per item
- `quantity` (int): Number of items to purchase
- `tax_rate` (float): Tax rate to apply  # MISMATCH: docs say tax_rate, code has discount

### Returns
- `float`: The total price including tax  # MISMATCH: code returns price after discount, not including tax

### Example
```python
total = calculate_total(10.0, 3, 0.1)
```

## process_order

Process an order with items.

### Parameters
- `order_id` (str): Unique order identifier
- `items` (list): List of items in the order
# MISSING: docs don't mention shipping parameter that exists in code

### Returns
- `str`: Confirmation message
"""

def test_analyze_endpoint():
    """Test the /api/v1/analyze endpoint."""
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/v1/analyze"
    
    payload = {
        "code_content": sample_code,
        "doc_content": sample_docs,
        "language": "python"
    }
    
    print("=" * 60)
    print("Testing /api/v1/analyze endpoint")
    print("=" * 60)
    print(f"\nEndpoint: {endpoint}")
    print(f"\nSample code has 2 functions:")
    print("  1. calculate_total(price, quantity, discount=0.0)")
    print("  2. process_order(order_id, items, shipping=True)")
    print(f"\nSample docs intentionally have mismatches...")
    print("\nSending request...\n")
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # LLM calls might take time
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "=" * 60)
            print("SUCCESS! Response received:")
            print("=" * 60)
            print(json.dumps(result, indent=2, default=str))
            
            # Pretty print summary
            print("\n" + "-" * 60)
            print("SUMMARY:")
            print("-" * 60)
            print(f"Status: {result.get('status')}")
            print(f"Summary: {result.get('summary')}")
            
            metadata = result.get('metadata', {})
            print(f"\nTrust Score: {metadata.get('trust_score')}%")
            print(f"Total Functions: {metadata.get('total_functions')}")
            print(f"Verified: {metadata.get('verified')}")
            
            discrepancies = result.get('discrepancies', [])
            print(f"\nDiscrepancies Found: {len(discrepancies)}")
            
            for i, disc in enumerate(discrepancies, 1):
                print(f"\n{i}. [{disc.get('severity').upper()}] {disc.get('type')}")
                print(f"   Description: {disc.get('description')}")
                if disc.get('code_snippet'):
                    print(f"   Code has: {disc.get('code_snippet')}")
                if disc.get('doc_snippet'):
                    print(f"   Docs say: {disc.get('doc_snippet')}")
                if disc.get('suggestion'):
                    print(f"   Suggestion: {disc.get('suggestion')}")
        else:
            print(f"\nERROR: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to server.")
        print("Make sure the FastAPI server is running:")
        print("  cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_analyze_endpoint()
