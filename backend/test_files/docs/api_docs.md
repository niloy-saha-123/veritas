# API Documentation

## calculate_total

Calculate the total price after applying a discount.

### Parameters
- `price` (float): The unit price per item
- `quantity` (int): Number of items to purchase
- `discount` (float): Discount rate to apply (default: 0.0)

### Returns
- `float`: The total price after discount

## process_order

Process an order with items.

### Parameters
- `order_id` (str): Unique order identifier
- `items` (list): List of items in the order
- `shipping` (bool): Whether to include shipping (default: True)

### Returns
- `str`: Confirmation message

## get_user_info

Get user information by ID.

### Parameters
- `user_id` (int): Unique user identifier
- `include_email` (bool): Whether to include email address (default: False)
- `include_avatar` (bool): Whether to include avatar URL  # EXTRA: not in code

### Returns
- `dict`: Dictionary containing user information

## delete_user

Remove a user from the system.

### Parameters
- `user_id` (int): User identifier
# MISSING: force parameter is not documented in docs

### Returns
- `bool`: True if successful
