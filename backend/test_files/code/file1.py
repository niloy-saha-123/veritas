"""Module 1: Order processing functions."""

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

def process_order(order_id: str, items: list, shipping: bool = True) -> str:
    """Process an order and return confirmation."""
    return f"Order {order_id} processed with {len(items)} items"

def apply_tax(amount: float, tax_rate: float = 0.1) -> float:
    """Apply tax to an amount."""
    return amount * (1 + tax_rate)
