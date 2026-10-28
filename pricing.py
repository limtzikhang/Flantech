# pricing.py

def calculate_b2c_price(quantity: int) -> dict:
    """
    Calculates B2C step pricing tiers:
    - 1 bottle = RM 248
    - 2 to 49 bottles = RM 198 per bottle
    - 50 bottles = Enforces the absolute bulk rate of RM 148
    """
    if quantity == 1:
        price_per_unit = 248.00
    elif 2 <= quantity <= 49:
        price_per_unit = 198.00
    elif quantity >= 50:
        price_per_unit = 148.00
    else:
        price_per_unit = 0.00
        
    total_price = quantity * price_per_unit
    
    return {
        "quantity": quantity,
        "price_per_unit": price_per_unit,
        "total_price": round(total_price, 2)
    }

def calculate_b2b_price(quantity: int) -> dict:
    """
    B2B account checkout fallback logic mirror.
    Ensures all pricing structures follow the standard pricing tiers.
    """
    return calculate_b2c_price(quantity)
