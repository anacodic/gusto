"""
Beer pairing tools for agent system.
"""
import json
import sys
import os
import requests
from typing import Optional

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
from services.beer_service import get_beer_recommender
from strands import tool


@tool
def check_menu_for_beer_tool(menu_url: str) -> str:
    """Check if restaurant menu contains beer items.
    
    Returns JSON with has_beer boolean and beer_items list.
    """
    print(f"🍺 [Menu Check] Checking menu: {menu_url}")
    
    if not menu_url:
        print(f"❌ [Menu Check] No menu URL provided")
        return json.dumps({"has_beer": False, "reason": "No menu URL"})
    
    try:
        print(f"📥 [Menu Check] Fetching menu from URL...")
        response = requests.get(menu_url, timeout=5)
        menu_text = response.text.lower()
        print(f"✅ [Menu Check] Menu fetched ({len(menu_text)} characters)")
        
        beer_keywords = ["beer", "ipa", "lager", "stout", "ale", "pilsner", "wheat", "porter"]
        beer_items = [kw for kw in beer_keywords if kw in menu_text]
        
        has_beer = len(beer_items) > 0
        if has_beer:
            print(f"✅ [Menu Check] Found beer items: {beer_items}")
        else:
            print(f"❌ [Menu Check] No beer items found in menu")
        
        return json.dumps({
            "has_beer": has_beer,
            "beer_items": beer_items,
            "menu_url": menu_url
        })
    except Exception as e:
        print(f"❌ [Menu Check] Error: {str(e)}")
        return json.dumps({"has_beer": False, "reason": str(e)})


@tool
def recommend_beer_pairing_tool(dish_name: str, taste_vector_json: str, menu_url: str = None) -> str:
    """Recommend beer pairing for a dish, checking menu first."""
    print(f"🍻 [Beer Pairing] Recommending beer for: '{dish_name}'")
    
    beer_recommender = get_beer_recommender()
    if beer_recommender is None:
        print(f"❌ [Beer Pairing] Beer recommender not available")
        return "Beer recommender not available"
    
    # Check menu for beer
    if menu_url:
        print(f"🔍 [Beer Pairing] Checking if restaurant serves beer...")
        menu_check_json = check_menu_for_beer_tool(menu_url)
        menu_check = json.loads(menu_check_json)
        if not menu_check.get("has_beer"):
            reason = menu_check.get('reason', 'No beer items found')
            print(f"❌ [Beer Pairing] Restaurant doesn't serve beer: {reason}")
            return f"Restaurant doesn't serve beer. Reason: {reason}"
        print(f"✅ [Beer Pairing] Restaurant serves beer, proceeding with recommendation")
    
    # Parse taste vector
    print(f"📊 [Beer Pairing] Parsing taste vector...")
    taste_data = json.loads(taste_vector_json)
    print(f"   Taste: sweet={taste_data['sweet']}, spicy={taste_data['spicy']}, umami={taste_data['umami']}")
    
    # Convert to beer feature format
    user_input = f"{dish_name} with taste: sweet={taste_data['sweet']}, spicy={taste_data['spicy']}, umami={taste_data['umami']}"
    
    try:
        print(f"🤖 [Beer Pairing] Calling ML beer recommender...")
        result = beer_recommender.get_recommendations(user_input)
        
        if result.get("recommendations"):
            beer_name = result["recommendations"][0]["name"]
            rating = result.get("predicted_rating", 0)
            print(f"✅ [Beer Pairing] Recommendation: {beer_name} (confidence: {rating:.2f}/5.0)")
            return f"Recommended pairing: {beer_name} (ML confidence: {rating:.1f}/5.0)"
        else:
            print(f"⚠️ [Beer Pairing] No recommendations returned")
            return "No beer recommendation available"
    except Exception as e:
        print(f"❌ [Beer Pairing] Error: {str(e)}")
        return f"Beer pairing error: {str(e)}"
