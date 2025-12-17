"""
Budget/price filtering tools for agent system.
"""
from strands import tool


@tool
def calculate_price_filter(max_price: float, price_per_person: bool = True) -> str:
    """Calculate price filter for Yelp search.
    
    Returns Yelp price scale: 1=$, 2=$$, 3=$$$, 4=$$$$
    """
    print(f"💰 [Price Filter] Calculating filter for ${max_price:.2f} {'per person' if price_per_person else 'total'}")
    
    if max_price <= 10:
        result = "1"
        price_level = "$"
    elif max_price <= 30:
        result = "1,2"
        price_level = "$-$$"
    elif max_price <= 60:
        result = "2,3"
        price_level = "$$-$$$"
    else:
        result = "3,4"
        price_level = "$$$-$$$$"
    
    print(f"✅ [Price Filter] Result: {result} ({price_level})")
    return result
