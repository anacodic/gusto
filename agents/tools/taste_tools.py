"""
Taste analysis tools for agent system.
Uses the exact same functions from swaad/backend/taste_analysis.py
"""
import json
import sys
import os
from typing import List, Dict, Optional

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import all taste analysis functions from swaad (via gusto services which match swaad exactly)
from services.taste_service import (
    infer_taste_from_text,
    infer_taste_from_groq,
    infer_taste_from_text_semantic,
    infer_taste_from_text_hybrid,
    taste_similarity,
    user_profile_to_taste_vector,
    favorites_boost
)
from strands import tool


@tool
def generate_taste_vector_tool(dish_name: str) -> str:
    """Generate 6D taste vector for a dish using keyword matching.
    
    Uses the same infer_taste_from_text function from swaad.
    
    Args:
        dish_name: Name of the dish to analyze
    
    Returns JSON: {"sweet": 0.0-1.0, "salty": 0.0-1.0, "sour": 0.0-1.0, 
                   "bitter": 0.0-1.0, "umami": 0.0-1.0, "spicy": 0.0-1.0}
    """
    print(f"👅 [Taste Vector] Analyzing: '{dish_name}'")
    
    # Try keyword matching first
    print(f"🔤 [Taste Vector] Trying keyword matching...")
    vector = infer_taste_from_text(dish_name)
    
    # If no match, use Groq AI
    if sum(vector) == 0:
        print(f"🤖 [Taste Vector] No keyword match, using Groq AI...")
        vector = infer_taste_from_groq(dish_name)
        print(f"✅ [Taste Vector] Groq AI generated taste profile")
    else:
        print(f"✅ [Taste Vector] Keyword matching found taste profile")
    
    result = {
        "sweet": round(vector[0], 3),
        "salty": round(vector[1], 3),
        "sour": round(vector[2], 3),
        "bitter": round(vector[3], 3),
        "umami": round(vector[4], 3),
        "spicy": round(vector[5], 3)
    }
    
    print(f"📊 [Taste Vector] Result: sweet={result['sweet']}, salty={result['salty']}, "
          f"sour={result['sour']}, bitter={result['bitter']}, umami={result['umami']}, spicy={result['spicy']}")
    
    return json.dumps(result)


@tool
def generate_taste_vector_groq_tool(dish_name: str) -> str:
    """Generate 6D taste vector for a dish using Groq AI.
    
    Uses the same infer_taste_from_groq function from swaad.
    
    Args:
        dish_name: Name of the dish to analyze
    
    Returns JSON: {"sweet": 0.0-1.0, "salty": 0.0-1.0, "sour": 0.0-1.0, 
                   "bitter": 0.0-1.0, "umami": 0.0-1.0, "spicy": 0.0-1.0}
    """
    print(f"🤖 [Taste Vector Groq] Analyzing: '{dish_name}'")
    vector = infer_taste_from_groq(dish_name)
    
    result = {
        "sweet": round(vector[0], 3),
        "salty": round(vector[1], 3),
        "sour": round(vector[2], 3),
        "bitter": round(vector[3], 3),
        "umami": round(vector[4], 3),
        "spicy": round(vector[5], 3)
    }
    
    return json.dumps(result)


@tool
def generate_taste_vector_semantic_tool(text: str) -> str:
    """Generate 6D taste vector using semantic search in Pinecone.
    
    Uses the same infer_taste_from_text_semantic function from swaad.
    
    Args:
        text: Text to analyze (dish name or ingredient description)
    
    Returns JSON: {"sweet": 0.0-1.0, "salty": 0.0-1.0, "sour": 0.0-1.0, 
                   "bitter": 0.0-1.0, "umami": 0.0-1.0, "spicy": 0.0-1.0}
    """
    print(f"🔍 [Taste Vector Semantic] Analyzing: '{text}'")
    vector = infer_taste_from_text_semantic(text)
    
    result = {
        "sweet": round(vector[0], 3),
        "salty": round(vector[1], 3),
        "sour": round(vector[2], 3),
        "bitter": round(vector[3], 3),
        "umami": round(vector[4], 3),
        "spicy": round(vector[5], 3)
    }
    
    return json.dumps(result)


@tool
def calculate_taste_similarity_tool(user_taste_vector: str, dish_taste_vector: str) -> str:
    """Calculate taste similarity between user and dish vectors.
    
    Uses the same taste_similarity function from swaad.
    
    Args:
        user_taste_vector: JSON string with user taste vector [sweet, salty, sour, bitter, umami, spicy]
        dish_taste_vector: JSON string with dish taste vector [sweet, salty, sour, bitter, umami, spicy]
    
    Returns JSON: {"similarity": 0.0-1.0, "percentage": 0.0-100.0}
    """
    try:
        user_vec = json.loads(user_taste_vector) if isinstance(user_taste_vector, str) else user_taste_vector
        dish_vec = json.loads(dish_taste_vector) if isinstance(dish_taste_vector, str) else dish_taste_vector
        
        # Convert dict to list if needed
        if isinstance(user_vec, dict):
            user_vec = [user_vec.get("sweet", 0), user_vec.get("salty", 0), user_vec.get("sour", 0),
                       user_vec.get("bitter", 0), user_vec.get("umami", 0), user_vec.get("spicy", 0)]
        if isinstance(dish_vec, dict):
            dish_vec = [dish_vec.get("sweet", 0), dish_vec.get("salty", 0), dish_vec.get("sour", 0),
                       dish_vec.get("bitter", 0), dish_vec.get("umami", 0), dish_vec.get("spicy", 0)]
        
        similarity = taste_similarity(user_vec, dish_vec)
        
        return json.dumps({
            "similarity": round(similarity, 4),
            "percentage": round(similarity * 100, 2)
        })
    except Exception as e:
        return json.dumps({"error": str(e), "similarity": 0.0, "percentage": 0.0})


@tool
def calculate_favorites_boost_tool(menu_items: List[str], favorite_dishes: List[Dict]) -> str:
    """Calculate boost score based on favorite dishes matching menu items.
    
    Uses the same favorites_boost function from swaad.
    
    Args:
        menu_items: List of menu item names
        favorite_dishes: List of dicts with "name" key for favorite dishes
    
    Returns JSON: {"boost": 0.0-1.0, "matches": int}
    """
    boost = favorites_boost(menu_items, favorite_dishes)
    # Count matches
    menu_lower = [m.lower() for m in menu_items]
    fav_names = [d.get("name", "").lower() for d in favorite_dishes if d.get("name")]
    matches = sum(1 for fav in fav_names if any(fav in menu for menu in menu_lower))
    
    return json.dumps({
        "boost": round(boost, 4),
        "matches": matches
    })
