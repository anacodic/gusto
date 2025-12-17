"""
Recommendation tools for agent system.
Uses the exact same functions from swaad/backend/recommendations.py
"""
import json
import sys
import os
from typing import List, Dict, Optional

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import all recommendation functions from swaad (via gusto services which match swaad exactly)
from services.recommendation_service import (
    dish_recommendations_for_restaurant,
    rank_restaurants,
    calculate_restaurant_taste_vector,
    filter_and_rank_recommendations
)
from strands import tool


@tool
def get_dish_recommendations_tool(
    menu_items: List[str],
    user_taste_vector: str,
    diet_type: Optional[str] = None,
    allergies: Optional[List[str]] = None,
    top_n: int = 5
) -> str:
    """Get recommended dishes from a restaurant's menu based on user taste preferences.
    
    Uses the same dish_recommendations_for_restaurant function from swaad.
    
    Args:
        menu_items: List of dish names (strings) or list of dicts with 'name' and 'taste' keys
        user_taste_vector: JSON string with user taste vector [sweet, salty, sour, bitter, umami, spicy]
        diet_type: Diet filter (veg, non-veg, mix) - optional
        allergies: List of user allergies - optional
        top_n: Number of top dishes to return (default: 5)
    
    Returns JSON: List of {"name": str, "similarity": float} objects sorted by similarity
    """
    try:
        # Parse user taste vector
        user_vec = json.loads(user_taste_vector) if isinstance(user_taste_vector, str) else user_taste_vector
        
        # Convert dict to list if needed
        if isinstance(user_vec, dict):
            user_vec = [user_vec.get("sweet", 0), user_vec.get("salty", 0), user_vec.get("sour", 0),
                       user_vec.get("bitter", 0), user_vec.get("umami", 0), user_vec.get("spicy", 0)]
        
        recommendations = dish_recommendations_for_restaurant(
            menu_items=menu_items,
            user_taste_vec=user_vec,
            diet_type=diet_type,
            allergies=allergies,
            top_n=top_n
        )
        
        return json.dumps(recommendations, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "recommendations": []})


@tool
def rank_restaurants_tool(
    restaurants: List[Dict],
    user_taste_vector: str,
    favorite_dishes: Optional[List[Dict]] = None
) -> str:
    """Rank restaurants based on taste similarity, favorites, and semantic match.
    
    Uses the same rank_restaurants function from swaad.
    
    Args:
        restaurants: List of restaurant dicts with 'score', 'taste_vector', 'menu_items' keys
        user_taste_vector: JSON string with user taste vector [sweet, salty, sour, bitter, umami, spicy]
        favorite_dishes: List of dicts with "name" key for favorite dishes - optional
    
    Returns JSON: List of restaurants sorted by combined score
    """
    try:
        # Parse user taste vector
        user_vec = json.loads(user_taste_vector) if isinstance(user_taste_vector, str) else user_taste_vector
        
        # Convert dict to list if needed
        if isinstance(user_vec, dict):
            user_vec = [user_vec.get("sweet", 0), user_vec.get("salty", 0), user_vec.get("sour", 0),
                       user_vec.get("bitter", 0), user_vec.get("umami", 0), user_vec.get("spicy", 0)]
        
        ranked = rank_restaurants(
            restaurants=restaurants,
            user_taste_vec=user_vec,
            favorite_dishes=favorite_dishes or []
        )
        
        return json.dumps(ranked, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e), "restaurants": []})


@tool
def calculate_restaurant_taste_vector_tool(menu_items: List[str]) -> str:
    """Calculate aggregate taste vector for a restaurant based on its menu.
    
    Uses the same calculate_restaurant_taste_vector function from swaad.
    
    Args:
        menu_items: List of menu item names
    
    Returns JSON: {"sweet": 0.0-1.0, "salty": 0.0-1.0, "sour": 0.0-1.0, 
                   "bitter": 0.0-1.0, "umami": 0.0-1.0, "spicy": 0.0-1.0}
    """
    try:
        taste_vec = calculate_restaurant_taste_vector(menu_items)
        
        result = {
            "sweet": round(taste_vec[0], 3),
            "salty": round(taste_vec[1], 3),
            "sour": round(taste_vec[2], 3),
            "bitter": round(taste_vec[3], 3),
            "umami": round(taste_vec[4], 3),
            "spicy": round(taste_vec[5], 3)
        }
        
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e), "taste_vector": [0.0] * 6})


@tool
def filter_and_rank_recommendations_tool(
    matches: List[Dict],
    user_taste_vector: str,
    favorite_dishes: Optional[List[Dict]] = None,
    diet_type: Optional[str] = None,
    allergies: Optional[List[str]] = None,
    max_results: int = 10,
    query_text: Optional[str] = None,
    location_filter: Optional[str] = None,
    cuisine_filter: Optional[str] = None,
    query_ingredients: Optional[List[str]] = None
) -> str:
    """Filter and rank restaurant recommendations from Pinecone matches.
    
    Uses the same filter_and_rank_recommendations function from swaad.
    
    Args:
        matches: List of Pinecone match results with metadata
        user_taste_vector: JSON string with user taste vector [sweet, salty, sour, bitter, umami, spicy]
        favorite_dishes: List of dicts with "name" key - optional
        diet_type: Diet filter (veg, non-veg, mix) - optional
        allergies: List of allergies - optional
        max_results: Maximum number of results to return (default: 10)
        query_text: Original query text - optional
        location_filter: Location filter string - optional
        cuisine_filter: Cuisine type filter - optional
        query_ingredients: List of ingredient names - optional
    
    Returns JSON: List of ranked restaurant recommendations
    """
    try:
        # Parse user taste vector
        user_vec = json.loads(user_taste_vector) if isinstance(user_taste_vector, str) else user_taste_vector
        
        # Convert dict to list if needed
        if isinstance(user_vec, dict):
            user_vec = [user_vec.get("sweet", 0), user_vec.get("salty", 0), user_vec.get("sour", 0),
                       user_vec.get("bitter", 0), user_vec.get("umami", 0), user_vec.get("spicy", 0)]
        
        ranked = filter_and_rank_recommendations(
            matches=matches,
            user_taste_vec=user_vec,
            favorite_dishes=favorite_dishes or [],
            diet_type=diet_type,
            allergies=allergies or [],
            max_results=max_results,
            query_text=query_text,
            location_filter=location_filter,
            cuisine_filter=cuisine_filter,
            query_ingredients=query_ingredients
        )
        
        return json.dumps(ranked, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e), "recommendations": []})
