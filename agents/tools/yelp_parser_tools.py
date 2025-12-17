"""
Yelp response parser tools for agent system.
Parses Yelp AI Chat API responses and maps them to frontend format.
"""
import json
import sys
import os
from typing import List, Dict, Optional

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from strands import tool


def convert_price_to_range(price: Optional[str]) -> Optional[int]:
    """Convert Yelp price string to numeric range. "$" -> 1, "$$" -> 2, etc."""
    if not price:
        return None
    return len(price)


@tool
def parse_yelp_response_tool(yelp_response_json: str) -> str:
    """Parse Yelp AI Chat API response and map to frontend format.
    
    Args:
        yelp_response_json: JSON string from Yelp AI Chat API response
    
    Returns:
        JSON string with restaurants in frontend format:
        {
            "restaurants": [
                {
                    "name": str,
                    "rating": float,
                    "price_range": int (1-4),
                    "cuisine_types": List[str],
                    "location": Dict,
                    "coordinates": Dict,
                    "recommended_dishes": List[Dict],
                    "photos": List[str],
                    "menu_url": str,
                    "url": str
                }
            ],
            "response_text": str,
            "chat_id": str
        }
    """
    try:
        # Parse Yelp response
        yelp_response = json.loads(yelp_response_json) if isinstance(yelp_response_json, str) else yelp_response_json
        
        # Extract response text and chat_id
        response_text = ""
        chat_id = None
        
        if "response" in yelp_response:
            response_text = yelp_response["response"].get("text", "")
        elif "text" in yelp_response:
            response_text = yelp_response["text"]
        
        chat_id = yelp_response.get("chat_id") or yelp_response.get("chatId")
        
        # Extract businesses from entities
        restaurants = []
        entities = yelp_response.get("entities", [])
        
        for entity in entities:
            businesses = entity.get("businesses", [])
            if not businesses:
                continue
            
            for business in businesses:
                try:
                    # Extract basic info
                    name = business.get("name", "")
                    rating = business.get("rating") or business.get("avg_rating", 0.0)
                    price = business.get("price", "")
                    price_range = convert_price_to_range(price)
                    
                    # Extract categories/cuisine types
                    categories = business.get("categories", [])
                    cuisine_types = []
                    if categories:
                        for cat in categories:
                            if isinstance(cat, dict):
                                cuisine_types.append(cat.get("title", cat.get("alias", "")))
                            else:
                                cuisine_types.append(str(cat))
                    
                    # Extract location
                    location = business.get("location", {})
                    location_dict = {}
                    if isinstance(location, dict):
                        location_dict = {
                            "address": location.get("address1") or location.get("address", ""),
                            "city": location.get("city", ""),
                            "state": location.get("state", ""),
                            "zip_code": location.get("zip_code") or location.get("zipCode", ""),
                            "country": location.get("country", "US"),
                            "formatted_address": business.get("formatted_address") or business.get("formattedAddress", "")
                        }
                    else:
                        location_dict = {"formatted_address": str(location) if location else ""}
                    
                    # Extract coordinates
                    latitude = business.get("latitude")
                    longitude = business.get("longitude")
                    coordinates = None
                    if latitude and longitude:
                        coordinates = {"latitude": float(latitude), "longitude": float(longitude)}
                    
                    # Extract photos
                    photos = []
                    contextual_info = business.get("contextual_info") or business.get("contextualInfo", {})
                    if contextual_info:
                        photos_list = contextual_info.get("photos", [])
                        if photos_list:
                            for photo in photos_list:
                                photo_url = photo.get("original_url") or photo.get("originalUrl", "")
                                if photo_url:
                                    photos.append(photo_url)
                    
                    # Extract menu URL
                    attributes = business.get("attributes", {})
                    menu_url = attributes.get("MenuUrl") or business.get("menu_url")
                    
                    # Extract URL
                    url = business.get("url", "")
                    
                    # Create recommended dishes based on cuisine (Yelp doesn't provide detailed menu)
                    recommended_dishes = []
                    if cuisine_types:
                        # Basic dish suggestions based on cuisine
                        cuisine_dishes = {
                            "pizza": ["Margherita Pizza", "Pepperoni Pizza", "Vegetarian Pizza"],
                            "italian": ["Pasta Carbonara", "Margherita Pizza", "Tiramisu"],
                            "sushi": ["Salmon Roll", "Tuna Roll", "California Roll"],
                            "japanese": ["Ramen", "Sushi", "Teriyaki"],
                            "chinese": ["Kung Pao Chicken", "Sweet and Sour Pork", "Fried Rice"],
                            "thai": ["Pad Thai", "Green Curry", "Tom Yum Soup"],
                            "mexican": ["Tacos", "Burrito", "Quesadilla"],
                            "indian": ["Butter Chicken", "Biryani", "Naan"],
                            "steak": ["Ribeye Steak", "Filet Mignon", "New York Strip"],
                            "seafood": ["Grilled Salmon", "Lobster", "Shrimp Scampi"]
                        }
                        
                        for cuisine in cuisine_types:
                            cuisine_lower = cuisine.lower()
                            for key, dishes in cuisine_dishes.items():
                                if key in cuisine_lower:
                                    recommended_dishes = [{"name": dish, "similarity": 75.0} for dish in dishes[:3]]
                                    break
                            if recommended_dishes:
                                break
                    
                    # Default dishes if none found
                    if not recommended_dishes:
                        recommended_dishes = [
                            {"name": "Chef's Special", "similarity": 70.0},
                            {"name": "Popular Dish", "similarity": 65.0}
                        ]
                    
                    restaurant = {
                        "id": business.get("id") or business.get("encid", ""),
                        "name": name,
                        "url": url,
                        "avg_rating": float(rating) if rating else None,
                        "price_range": price_range,
                        "cuisine_types": cuisine_types,
                        "location": location_dict,
                        "coordinates": coordinates,
                        "menu_items": [],  # Yelp doesn't provide detailed menu items
                        "popular_dishes": [d.get("name") for d in recommended_dishes],
                        "taste_vector": [0.0] * 6,  # Will be calculated if needed
                        "recommended_dishes": recommended_dishes[:5],  # Limit to 5
                        "photos": photos[:5] if photos else None,
                        "menu_url": menu_url,
                        "score": float(rating) if rating else 0.0
                    }
                    
                    restaurants.append(restaurant)
                except Exception as e:
                    print(f"❌ [Yelp Parser] Error parsing business: {e}")
                    continue
        
        # Sort by rating (score) descending
        restaurants.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        
        result = {
            "restaurants": restaurants,
            "response_text": response_text,
            "chat_id": chat_id
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        print(f"❌ [Yelp Parser] Error: {str(e)}")
        return json.dumps({"error": str(e), "restaurants": []})
