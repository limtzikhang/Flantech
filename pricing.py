# pricing.py

BASE_PRICE = 248.00  # Standard Retail B2C price
B2B_PRICE = 148.00   # Discounted B2B package price

def calculate_b2c_price(quantity: int) -> dict:
    """Calculates B2C cost structure."""
    total_price = quantity * BASE_PRICE
    return {
        "quantity": quantity,
        "price_per_unit": BASE_PRICE,
        "total_price": round(total_price, 2)
    }

def calculate_b2b_price(quantity: int) -> dict:
    """
    Calculates B2B cost structure. Enforces a bulk rate of RM148 
    if they hit the 50-bottle network standard.
    """
    if quantity >= 50:
        price_per_unit = B2B_PRICE
    else:
        price_per_unit = BASE_PRICE
        
    total_price = quantity * price_per_unit
    return {
        "quantity": quantity,
        "price_per_unit": price_per_unit,
        "total_price": round(total_price, 2)
    }
