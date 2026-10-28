# pricing.py

# Tier thresholds
B2C_BULK_THRESHOLD = 6
B2B_BULK_THRESHOLD = 50

# Base pricing configuration (adjust these values to your exact math)
BASE_PRICE_PER_BOTTLE = 100.00  # Standard single-bottle retail price
B2C_BULK_DISCOUNT = 0.10        # 10% off for 6+ bottles
B2B_BULK_DISCOUNT = 0.30        # 30% off for 50+ bottles

def calculate_b2c_price(quantity: int) -> dict:
    """
    Calculates B2C pricing with a discount tier starting at 6 bottles.
    """
    price_per_unit = BASE_PRICE_PER_BOTTLE
    is_bulk = quantity >= B2C_BULK_THRESHOLD
    
    if is_bulk:
        price_per_unit = BASE_PRICE_PER_BOTTLE * (1 - B2C_BULK_DISCOUNT)
        
    total_price = quantity * price_per_unit
    
    return {
        "quantity": quantity,
        "price_per_unit": round(price_per_unit, 2),
        "total_price": round(total_price, 2),
        "bulk_applied": is_bulk
    }

def calculate_b2b_price(quantity: int) -> dict:
    """
    Calculates B2B pricing with heavy discount tiers starting at 50 bottles.
    """
    price_per_unit = BASE_PRICE_PER_BOTTLE
    is_bulk = quantity >= B2B_BULK_THRESHOLD
    
    if is_bulk:
        price_per_unit = BASE_PRICE_PER_BOTTLE * (1 - B2B_BULK_DISCOUNT)
    else:
        # Optional: Set a smaller discount if a business buys less than 50
        price_per_unit = BASE_PRICE_PER_BOTTLE * 0.85 
        
    total_price = quantity * price_per_unit
    
    return {
        "quantity": quantity,
        "price_per_unit": round(price_per_unit, 2),
        "total_price": round(total_price, 2),
        "bulk_applied": is_bulk
    }

# FUTURE IMPLEMENTATION STUB
# def calculate_mlm_commissions(quantity, user_tier):
#     pass
