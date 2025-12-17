"""
Dish processing tools for agent system.
Uses the exact same functions from swaad/backend/dish_processing.py
"""
import json
import sys
import os
from typing import List, Optional, Dict, Tuple

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import all dish processing functions from swaad (via gusto services which match swaad exactly)
from services.restaurant_service import (
    filter_dishes_by_diet,
    detect_diet_from_query,
    classify_dish_diet_with_groq,
    classify_dish_with_groq,
    normalize_dish_name,
    extract_dish_from_query,
    extract_location_from_query,
    classify_intent,
    is_relevant_query,
    check_location_match,
    validate_dishes_with_groq,
    extract_dish_and_restaurant,
    is_nonveg_text
)
from strands import tool


@tool
def filter_dishes_by_diet_tool(dishes: List[str], diet_type: Optional[str]) -> str:
    """Filter dishes based on dietary preferences.
    
    Uses the same filter_dishes_by_diet function from swaad.
    
    Args:
        dishes: List of dish names
        diet_type: Diet filter (veg, non-veg, mix, any, all) - None means no filter
    
    Returns JSON: {"filtered_dishes": List[str], "count": int}
    """
    try:
        filtered = filter_dishes_by_diet(dishes, diet_type)
        return json.dumps({
            "filtered_dishes": filtered,
            "count": len(filtered),
            "original_count": len(dishes)
        })
    except Exception as e:
        return json.dumps({"error": str(e), "filtered_dishes": [], "count": 0})


@tool
def detect_diet_from_query_tool(query: str) -> str:
    """Detect diet preference from query string using Groq.
    
    Uses the same detect_diet_from_query function from swaad.
    
    Args:
        query: User query string
    
    Returns JSON: {"diet_type": "veg" | "non-veg" | null}
    """
    try:
        diet = detect_diet_from_query(query)
        return json.dumps({"diet_type": diet})
    except Exception as e:
        return json.dumps({"error": str(e), "diet_type": None})


@tool
def classify_dish_diet_tool(dish_name: str) -> str:
    """Classify a dish as 'veg' or 'non-veg' using Groq LLM.
    
    Uses the same classify_dish_diet_with_groq function from swaad.
    
    Args:
        dish_name: Name of the dish to classify
    
    Returns JSON: {"classification": "veg" | "non-veg"}
    """
    try:
        classification = classify_dish_diet_with_groq(dish_name)
        return json.dumps({"classification": classification})
    except Exception as e:
        return json.dumps({"error": str(e), "classification": "veg"})


@tool
def classify_dish_category_tool(dish_name: str) -> str:
    """Classify dish into category using Groq AI.
    
    Uses the same classify_dish_with_groq function from swaad.
    
    Args:
        dish_name: Name of the dish to classify
    
    Returns JSON: {"category": "appetizer" | "mains" | "desserts"}
    """
    try:
        category = classify_dish_with_groq(dish_name)
        return json.dumps({"category": category})
    except Exception as e:
        return json.dumps({"error": str(e), "category": "mains"})


@tool
def normalize_dish_name_tool(name: str) -> str:
    """Normalize dish name for comparison.
    
    Uses the same normalize_dish_name function from swaad.
    
    Args:
        name: Dish name to normalize
    
    Returns JSON: {"normalized": str}
    """
    try:
        normalized = normalize_dish_name(name)
        return json.dumps({"normalized": normalized})
    except Exception as e:
        return json.dumps({"error": str(e), "normalized": name})


@tool
def extract_dish_from_query_tool(query: str) -> str:
    """Extract the specific dish name from a user query using regex and Groq.
    
    Uses the same extract_dish_from_query function from swaad.
    
    Args:
        query: User query string
    
    Returns JSON: {"dish": str | null}
    """
    try:
        dish = extract_dish_from_query(query)
        return json.dumps({"dish": dish})
    except Exception as e:
        return json.dumps({"error": str(e), "dish": None})


@tool
def extract_location_from_query_tool(query: str) -> str:
    """Extract location from the query text.
    
    Uses the same extract_location_from_query function from swaad.
    
    Args:
        query: User query string
    
    Returns JSON: {"location": str | null}
    """
    try:
        location = extract_location_from_query(query)
        return json.dumps({"location": location})
    except Exception as e:
        return json.dumps({"error": str(e), "location": None})


@tool
def classify_intent_tool(query: str) -> str:
    """Classify user intent using Groq.
    
    Uses the same classify_intent function from swaad.
    
    Args:
        query: User query string
    
    Returns JSON: {"intent": "dish_search" | "restaurant_search" | "greeting" | "other"}
    """
    try:
        intent = classify_intent(query)
        return json.dumps({"intent": intent})
    except Exception as e:
        return json.dumps({"error": str(e), "intent": "other"})


@tool
def is_relevant_query_tool(query: str) -> str:
    """Check if query is relevant to food/restaurant search using Groq AI.
    
    Uses the same is_relevant_query function from swaad.
    
    Args:
        query: User query string
    
    Returns JSON: {"is_relevant": bool}
    """
    try:
        is_relevant = is_relevant_query(query)
        return json.dumps({"is_relevant": is_relevant})
    except Exception as e:
        return json.dumps({"error": str(e), "is_relevant": True})


@tool
def check_location_match_tool(user_location: str, restaurant_location: str) -> str:
    """Check if user location matches restaurant location using Groq.
    
    Uses the same check_location_match function from swaad.
    
    Args:
        user_location: User's location string
        restaurant_location: Restaurant's location string
    
    Returns JSON: {"matches": bool}
    """
    try:
        matches = check_location_match(user_location, restaurant_location)
        return json.dumps({"matches": matches})
    except Exception as e:
        return json.dumps({"error": str(e), "matches": False})


@tool
def validate_dishes_tool(items: List[str]) -> str:
    """Use Groq to intelligently filter out non-dish items from extracted menu text.
    
    Uses the same validate_dishes_with_groq function from swaad.
    
    Args:
        items: List of potential dish names
    
    Returns JSON: {"valid_dishes": List[str], "count": int}
    """
    try:
        valid_dishes = validate_dishes_with_groq(items)
        return json.dumps({
            "valid_dishes": valid_dishes,
            "count": len(valid_dishes),
            "original_count": len(items)
        })
    except Exception as e:
        return json.dumps({"error": str(e), "valid_dishes": [], "count": 0})


@tool
def extract_dish_and_restaurant_tool(query: str) -> str:
    """Extract dish and restaurant name from query using Groq.
    
    Uses the same extract_dish_and_restaurant function from swaad.
    
    Args:
        query: User query string
    
    Returns JSON: {"dish": str | null, "restaurant": str | null}
    """
    try:
        result = extract_dish_and_restaurant(query)
        if result:
            dish, restaurant = result
            return json.dumps({"dish": dish, "restaurant": restaurant})
        else:
            return json.dumps({"dish": None, "restaurant": None})
    except Exception as e:
        return json.dumps({"error": str(e), "dish": None, "restaurant": None})


@tool
def is_nonveg_text_tool(text: str) -> str:
    """Check if text contains non-vegetarian keywords.
    
    Uses the same is_nonveg_text function from swaad.
    
    Args:
        text: Text to check
    
    Returns JSON: {"is_nonveg": bool}
    """
    try:
        is_nonveg = is_nonveg_text(text)
        return json.dumps({"is_nonveg": is_nonveg})
    except Exception as e:
        return json.dumps({"error": str(e), "is_nonveg": False})
